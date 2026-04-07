# Bits OpenAPI Real Access Reference

## Standard runtime inputs

Recommended env vars:

```bash
export BITS_SA_SECRET='<service_account_secret>'
export BITS_USERNAME='sunjunhao.39'
export BITS_DOMAIN='pipelines_open;v1'
```

Optional:

```bash
export BITS_PIPELINE_ID='656265707522'
export BITS_RUN_ID=''
export BITS_JOB_RUN_ID=''
```

## Standard verification sequence

### 1. Exchange JWT

```bash
curl -i -H "Authorization: Bearer ${BITS_SA_SECRET}" \
  https://cloud.bytedance.net/auth/api/v1/jwt
```

Read:

- `X-Jwt-Token`

### 2. Verify pipeline access

```bash
curl "https://bits.bytedance.net/api/v1/pipelines/open/${BITS_PIPELINE_ID}" \
  -H "x-jwt-token: ${CLOUD_JWT}" \
  -H "username: ${BITS_USERNAME}" \
  -H "domain: ${BITS_DOMAIN}"
```

### 3. Verify run access

```bash
curl "https://bits.bytedance.net/api/v1/pipelines/open/runs/${BITS_RUN_ID}" \
  -H "x-jwt-token: ${CLOUD_JWT}" \
  -H "username: ${BITS_USERNAME}" \
  -H "domain: ${BITS_DOMAIN}"
```

### 4. Verify job access

```bash
curl "https://bits.bytedance.net/api/v1/pipelines/open/job_runs/${BITS_JOB_RUN_ID}?need_logs=true&need_outputs=true" \
  -H "x-jwt-token: ${CLOUD_JWT}" \
  -H "username: ${BITS_USERNAME}" \
  -H "domain: ${BITS_DOMAIN}"
```

## 401 troubleshooting

If Bits returns `401`, check:

- did you exchange the secret for a JWT first
- are you really sending `x-jwt-token`, not the raw secret
- is the JWT expired
- is the `domain` header malformed or missing

## 403 troubleshooting

If Bits returns `403`, check:

- whether the service account has `pipelines_open:v1` permission
- whether the target space granted the service account resource access
- whether the endpoint is marked as “申请接入”

## Compact prompt for another agent

```text
Use $bits-openapi-real-access to switch from mock mode to real Bits access.

Inputs:
- BITS_SA_SECRET
- BITS_USERNAME=sunjunhao.39
- optional pipeline_id/run_id/job_run_id

Required flow:
1. Exchange BITS_SA_SECRET for X-Jwt-Token via cloud.bytedance.net/auth/api/v1/jwt
2. Use the returned JWT as x-jwt-token
3. Call Bits OpenAPI with:
   - x-jwt-token
   - username: sunjunhao.39
   - domain: pipelines_open;v1
4. Validate GetPipeline first
5. If 401, treat as auth/header issue
6. If 403, treat as permission issue
7. Do not hide real blockers behind mock success
```
