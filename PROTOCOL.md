# About the web portal

1. Overview

Urja Meter Ops is an internal web portal used by electricity distribution utility staff to access smart meter information. The objective is to expose its existing read-only functionality through a clean REST API, allowing other systems to retrieve meter information programmatically without interacting with the portal's UI.

2. Data

The API integration is designed to expose the following information, subject to what the portal actually provides:

Meter information: Meter number or unique identifier and associated details.
Network location: Information linking a meter to its network location, where available.
Meter status: Operational status, if provided by the portal.
Recent consumption: Available consumption readings and associated timestamps, if exposed by the portal.

3. Accessing the Data

The intended integration approach is to have a backend service communicate with the existing portal and translate its responses into structured JSON.

The proposed API exposes three read-only operations:

GET /api/v1/meters — List meters, with optional filtering and pagination.
GET /api/v1/meters/search?meter_number=<number> — Search for meters by meter number.
GET /api/v1/meters/{meter_id} — Retrieve information for a specific meter.

These are the proposed API contracts; their implementation must be aligned with the portal's actual request and response formats.

4. Authentication and Access

The new API uses Bearer token authentication to control access to its endpoints. The token is configured through an environment variable rather than hardcoded into the source code.

Access to the underlying Urja portal is a separate concern. Its authentication mechanism—such as session cookies, form-based login, or single sign-on—must be established by inspecting the actual portal and its authorized network requests. The API should manage upstream authentication internally without exposing portal credentials or session cookies to API consumers
