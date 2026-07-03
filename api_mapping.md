# Security Vendor API Endpoints Mapping

This document maps the specific functional requirements to the respective vendor APIs for the Security Bridge integration.

## 1. Phishing-Training (Phishing Results)
**Endpoint:** `GET /v1/phishing/security_tests` or `GET /v1/phishing/campaigns/{campaign_id}/users`
**Base URL:** `https://us.api.phishing-training.com` (Note: Depends on your data center, e.g., `eu.api.phishing-training.com`)
**Authentication:** Bearer Token (API Key generated via KMSAT Admin Console)
**Usage:** Used to retrieve the results of phishing campaigns, including which users clicked, opened, or reported the emails.

## 2. Security-Portal (Managed Alerts)
**Note:** Security-Portal manages detection and response actively through their SOC. Customers review managed alerts via the **Security-Portal Atlas Platform** or **Insight Portal**.
**There is no public REST API documented specifically for retrieving your managed security alerts directly**.
*Workaround:* Alerts are typically ingested via forwarding or viewed in the portal. Security-Portal's Threat Intelligence API serves IOCs but not the direct managed alerts lifecycle. For integration, a custom Webhook or API forwarding from the Atlas Platform might be required.

## 3. EDR-Provider (Threat Detections)
**Endpoint:** `GET /web/api/v2.1/threats`
**Authentication:** API Token (Generated in the EDR-Provider Management Console)
**Usage:** Retrieves threat detections. Supports filtering by various parameters such as agent, OS, analyst verdicts, and incident statuses.

## 4. SumoLogic (Saved Search Results)
**Endpoint:** `POST /api/v1/search/jobs` (to execute) and `GET /api/v1/search/jobs/{searchJobId}/records` (to fetch results)
**Base URL:** `https://api.[DEPLOYMENT].sumologic.com` (Where DEPLOYMENT is us2, eu, etc.)
**Authentication:** Basic Auth (Access ID and Access Key)
**Usage:** SumoLogic has a "Log Searches Management API" for saving searches, but to get *results*, you use the Search Job API to asynchronously execute a log search query and pull the resulting records.

## 5. Google Workspace (Mail Phishing Alerts) - *Planned*
**API:** Google Alert Center API (`googleapis.alertcenter`)
**Authentication:** Google Service Account (`google-auth-library`)
**Usage:** Polling the Google Alert Center API for `MailPhishing` type alerts.
