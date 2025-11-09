import os
import json
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env"), override=True)

# Optional: set CORS headers explicitly
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PATCH,DELETE,OPTIONS")
    return response


'''
!! NOTE: Running this will DROP all records and start your DB from scratch.
!! Uncomment ONLY on first run to initialize the database with the seed drink.
'''
# db_drop_and_create_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_json_request():
    """Safely parse request body as JSON, raising 400 if invalid/missing."""
    body = request.get_json(silent=True)
    if body is None:
        abort(400, description="Request does not contain a valid JSON body")
    return body


def get_drink_or_404(drink_id: int) -> Drink:
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404, description=f"Drink with id={drink_id} not found")
    return drink


def to_json_recipe(value):
    """Ensure recipe is stored as JSON string (Drink model expects string)."""
    # Accept either a dict or list from client; store as JSON string
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    # If client already sent a JSON string, keep it
    if isinstance(value, str):
        # Basic sanity: ensure it parses as JSON
        try:
            json.loads(value)
            return value
        except Exception:
            abort(400, description="Field 'recipe' must be valid JSON")
    abort(400, description="Field 'recipe' must be an object or array")


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

# GET /drinks (public) – short representation
@app.route("/drinks", methods=["GET"])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id.asc()).all()
        return jsonify({
            "success": True,
            "drinks": [d.short() for d in drinks]
        }), 200
    except Exception:
        abort(500)


# GET /drinks-detail – requires 'get:drinks-detail' – long representation
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(_payload):
    try:
        drinks = Drink.query.order_by(Drink.id.asc()).all()
        return jsonify({
            "success": True,
            "drinks": [d.long() for d in drinks]
        }), 200
    except Exception:
        abort(500)


# POST /drinks – requires 'post:drinks'
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(_payload):
    body = parse_json_request()
    title = body.get("title")
    recipe = body.get("recipe")

    if not title:
        abort(400, description="Missing required field: 'title'")
    if recipe is None:
        abort(400, description="Missing required field: 'recipe'")

    try:
        drink = Drink(title=title.strip(), recipe=to_json_recipe(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except exc.SQLAlchemyError:
        abort(422)
    except Exception:
        abort(500)


# PATCH /drinks/<id> – requires 'patch:drinks'
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(_payload, drink_id):
    drink = get_drink_or_404(drink_id)
    body = parse_json_request()

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    if title is None and recipe is None:
        abort(400, description="Provide at least one of: 'title', 'recipe'")

    try:
        if title is not None:
            drink.title = title.strip()
        if recipe is not None:
            drink.recipe = to_json_recipe(recipe)

        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except exc.SQLAlchemyError:
        abort(422)
    except Exception:
        abort(500)


# DELETE /drinks/<id> – requires 'delete:drinks'
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(_payload, drink_id):
    drink = get_drink_or_404(drink_id)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200
    except exc.SQLAlchemyError:
        abort(422)
    except Exception:
        abort(500)


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": getattr(error, "description", "bad request")
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": getattr(error, "description", "unauthorized")
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": getattr(error, "description", "forbidden")
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": getattr(error, "description", "resource not found")
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def handle_auth_error(err: AuthError):
    """
    AuthError handler: returns JSON with the original status code from AuthError.
    AuthError is expected to have: error (dict/message) and status_code (int).
    """
    status = getattr(err, "status_code", 401)
    description = None
    # Prefer explicit message if present
    if isinstance(getattr(err, "error", None), dict):
        description = err.error.get("description") or err.error.get("code")
    elif isinstance(getattr(err, "error", None), str):
        description = err.error

    return jsonify({
        "success": False,
        "error": status,
        "message": description or "authentication/authorization error"
    }), status
