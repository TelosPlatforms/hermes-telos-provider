# Telos model provider for Hermes

Sign in to Telos through Hermes browser authorization, or use an existing API key. Hermes owns Chat Completions transport.
The picker lists authenticated canonical models and workspace routers. Telos chooses each model's lowest-cost eligible provider and retains compatible same-model providers for failover.

## Setup

```sh
hermes plugins install telos
hermes auth add telos
hermes model
```

`hermes auth add telos` opens Telos in your browser. Sign in, review the
Inference API permission, and approve. Telos creates a key named **Hermes**,
limited to `inference:write` and expiring in 90 days; Hermes stores it in its
credential pool. Then select **Telos** and a model or workspace router in
`hermes model`. An existing API key can be entered through Hermes's credential
prompt instead. The key needs Inference API access and permission to use the
selected workspace router. Subscription, wallet, and workspace policy checks still apply.

Telos keys do not refresh. After expiry or revocation, run `hermes auth add telos`
again. `hermes auth logout telos` removes only local credentials; revoke keys in
Telos under Platform → API keys.

The default endpoint is `https://app.telosplatforms.com/v1`. For another
authorized Telos endpoint, set `TELOS_BASE_URL` to its origin followed by `/v1`
before `hermes auth add telos`, and enter the same URL at the **Base URL** prompt
in `hermes model`. `TELOS_API_KEY` is resolved and stored by Hermes; do not put
secrets in this plugin or shell history.

## Models and reasoning

The model picker lists every router returned by authenticated `/v1/models` first,
then every available canonical model, by ID (`route:orbit` is the balanced router).
There is no packaged shortlist, alias table, or static fallback catalogue.
Telos may change the serving provider, but never the model you selected. An
unavailable model returns a typed error.

A reasoning effort you set in Hermes is sent as `reasoning_effort`; Telos fits it
to the selected model. With no effort set, a router chooses its configured effort.

Capabilities, context/output limits and fixed router prices are not guessed.
Hermes may use its own metadata heuristics. Router pricing is variable; use Telos's
billing records for actual charges, not an assumed zero cost in the harness.

## Data and permissions disclosure

Hermes sends authenticated model-discovery and inference requests to the configured
Telos endpoint. Telos routes inference to the upstream providers permitted by your
workspace policy. Browser login uses Hermes's standard PKCE helper, which stores the
credential in Hermes's credential pool. The plugin does not install dependencies,
execute shell commands, start background services, patch Hermes, or send telemetry to another destination. Inference requests include the stable Hermes conversation ID as `metadata.conversation_id` so Telos can group them in Eval Suite Activity. Content remains subject to workspace capture settings.
Hermes owns credential storage and all HTTP transport. Existing Hermes approval behavior applies.

## Removal

Stop active requests and select another provider with `hermes model`. Then run
`hermes plugins remove telos`, or remove only this plugin directory. Credentials,
conversations and other profile configuration are retained. Do not delete a
profile to uninstall the provider.
