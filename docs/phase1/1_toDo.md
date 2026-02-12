# Phase 1: Bare Minimum Vertical Slice - Task List

**Duration:** 2 weeks  
**Goal:** Build complete end-to-end flow from API to database

---

## Priority Tasks

### High Priority (Must Complete)

- [x] **1. Create API Gateway in CDK** ✅
  - [x] Create REST API resource
  - [x] Add POST /v1/events endpoint
  - [x] Configure CORS
  - [x] Create SNS Topic (for Task 5)
  - [x] Connect SNS → SQS (for Task 5)

- [ ] **2. Setup Cognito (or Mock Authentication)**
  - Create Cognito user pool (or use mock for local dev)
  - Generate test JWT tokens
  - Configure API Gateway authorizer

- [ ] **3. Add Payload Validation**
  - Validate required fields: `event_type`, `occurred_at`, `source`, `payload`
  - Return 400 for invalid payloads
  - Return descriptive error messages

- [ ] **4. Update Ingress Lambda Handler**
  - Parse incoming request
  - Validate payload
  - Generate `event_id` (UUID)
  - Build event envelope
  - Return 202 with event_id

- [ ] **5. Create SNS Topic in CDK**
  - Create SNS topic for event distribution
  - Link to event ingestion workflow
  - Configure message filtering (optional)

- [ ] **6. Connect SNS → SQS in CDK**
  - Create SNS subscription to SQS queue
  - Ensure SNS publishes to existing SQS queue
  - Configure message attributes

- [ ] **7. Update Consumer Lambda Handler**
  - Receive SQS messages (batch mode)
  - Parse event envelope
  - Extract projection data
  - Store in database
  - Handle errors gracefully

- [ ] **8. Create Database Connection Utilities**
  - Create connection pooling utility
  - Add query execution helpers
  - Implement connection error handling

- [ ] **9. Store Data in raw_events Table**
  - Insert complete event JSON
  - Store event_id, event_version, payload_json, ingested_at
  - Handle duplicates (unique constraint on event_id)

- [ ] **10. Store Data in projections Table**
  - Create projection from raw event
  - Store consumer_name, event_id, projection_json, processed_at
  - Maintain unique constraint on (consumer_name, event_id)

---

### Medium Priority (Important)

- [ ] **11. Add Structured Logging**
  - JSON-formatted logs
  - Include event_id correlation
  - Log request/response in API
  - Log processing in consumer

- [ ] **12. Add Integration Tests**
  - Test API endpoint with valid payload
  - Test API endpoint with invalid payload
  - Test database persistence
  - Test end-to-end flow

- [ ] **13. Update Unit Tests**
  - Update ingress handler tests
  - Update consumer handler tests
  - Mock SNS/SQS for testing

- [ ] **14. Create Database Migration**
  - Update Alembic scripts if needed
  - Verify raw_events table exists
  - Verify projections table exists

- [ ] **15. Update CDK Stack**
  - Add API Gateway to baseline_stack.py
  - Add SNS topic
  - Add Cognito configuration
  - Add IAM roles/permissions

---

### Low Priority (Nice to Have)

- [ ] **16. Add API Documentation**
  - Document API contract (OpenAPI/Swagger)
  - Document request/response formats
  - Document error codes

- [ ] **17. Add Error Handling**
  - Handle API errors gracefully
  - Return meaningful error messages
  - Log errors for debugging

- [ ] **18. Performance Optimization**
  - Batch database inserts if needed
  - Optimize queries
  - Monitor Lambda execution time

- [ ] **19. Add Monitoring**
  - Add CloudWatch metrics
  - Add CloudWatch alarms
  - Track API latency

- [ ] **20. Update README**
  - Document Phase 1 implementation
  - Update API usage examples
  - Update local testing instructions

---

## Exit Criteria Verification

Before marking Phase 1 complete, verify:

- [ ] Valid request returns `202` with `event_id`
  - Test with: `curl -X POST http://api/v1/events -d '{...}'`

- [ ] Invalid request returns `400` with error details
  - Test with: missing required fields, invalid data types

- [ ] `raw_events` table populated
  - Query: `SELECT COUNT(*) FROM raw_events;`

- [ ] `projections` table populated
  - Query: `SELECT COUNT(*) FROM projections;`

- [ ] Structured logs with correlation
  - Check: CloudWatch logs contain event_id in all messages

- [ ] All tests pass
  - Run: `pytest -v`

- [ ] Code quality checks pass
  - Run: `ruff check .`

---

## Testing Checklist

| Test | Command | Expected Result |
|------|---------|-----------------|
| Unit Tests | `pytest tests/ -v` | All pass ✅ |
| Code Quality | `ruff check .` | No issues ✅ |
| API Valid | `POST /v1/events (valid)` | 202 response |
| API Invalid | `POST /v1/events (invalid)` | 400 response |
| Database | `SELECT * FROM raw_events LIMIT 1` | Record exists |
| Logs | Check CloudWatch | JSON logs with event_id |

---

## Architecture Reminder

```
Client → API Gateway → Ingress Lambda → SNS Topic → SQS Queue → Consumer Lambda → PostgreSQL
```

**Key Flow:**
1. Client sends POST to `/v1/events`
2. API Gateway validates JWT token
3. Ingress Lambda validates payload, generates event_id
4. Event published to SNS
5. SNS sends to SQS queue
6. Consumer Lambda triggered automatically
7. Consumer stores in PostgreSQL

---

## Notes

- Use local PostgreSQL (docker-compose) for development
- Mock AWS services (SQS, SNS, Cognito) in tests with `moto`
- Keep Cognito simple - can switch to real config later
- All code should have unit tests
- Update CI/CD as needed for new code

---

## Next Steps

1. Start with tasks 1-5 (API setup and validation)
2. Then tasks 6-10 (SNS/SQS and database)
3. Finally tasks 11-14 (testing and logging)
4. Verify exit criteria before completing phase

**Ready to start? Pick the first task above! 🚀**
