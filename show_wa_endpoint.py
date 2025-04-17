from worldathletics import WorldAthletics

wa = WorldAthletics()
# most wrappers expose the GraphQL URL here
print("WorldAthletics GraphQL endpoint:", getattr(wa, "url", None))
# and possibly the HTTP client base URL
print("HTTP client base:", getattr(wa, "http_client", None))
