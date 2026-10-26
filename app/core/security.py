from flask import abort, request

CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self'",
        "font-src 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "base-uri 'none'",
        "object-src 'none'",
        "require-trusted-types-for 'script'",
        "trusted-types board",
    ]
)

SECURITY_HEADERS = {
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cache-Control": "no-store",
}
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
OTHER_SITES = {"cross-site", "same-site"}


SMALL_BODY_LIMIT = 16 * 1024


def block_other_sites():
    if request.method in UNSAFE_METHODS and request.headers.get("Sec-Fetch-Site") in OTHER_SITES:
        abort(403)


def limit_body_size():
    if request.mimetype != "multipart/form-data":
        request.max_content_length = SMALL_BODY_LIMIT
        if (request.content_length or 0) > SMALL_BODY_LIMIT:
            abort(413)


def add_security_headers(response):
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


def init_app(app):
    app.before_request(block_other_sites)
    app.before_request(limit_body_size)
    app.after_request(add_security_headers)
