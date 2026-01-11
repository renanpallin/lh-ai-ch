# DocProc Findings

Issues found during code review and the fixes I applied.

**Database update required:**
```bash
docker compose exec db psql -U postgres -d docproc -c "ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';"
```


## How to test

Run `docker compose up` and access the application at `http://localhost:5173`. You can upload PDF documents with tags, filter by tag using the dropdown in the header, and search within the document content. The seed script at `scripts/seed_data.py` can be used to populate the database with sample documents and tags for testing.


## Backend

### `[SECURITY]` SQL Injection in `/search`

A user could extract data from the database through the search endpoint.
I verified this vulnerability by testing injection payloads and was able to access data from other tables in the database, not just the documents table.
Fixed by using SQLAlchemy ORM instead of raw SQL. The ORM properly escapes query parameters.


### `[SECURITY]` Path Traversal in file upload

A malicious user could upload files outside the intended directory by sending a filename containing `../`. I tested this vulnerability using the curl command below and confirmed the file was written outside the upload directory:

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@/tmp/test.pdf;filename=../../../app/HACKED.pdf"
```

Fixed by validating the filename with `os.path.basename()` and checking the final path stays within the upload directory.


### `[SECURITY]` Hardcoded secrets

`SECRET_KEY` had a hardcoded default value in `config.py`. Removed it and moved to `docker-compose.yml` as an environment variable.


### `[SECURITY]` CORS too permissive

CORS was set to `allow_origins=["*"]`. Changed to use specific origins via `ALLOWED_ORIGINS` env var, defaulting to localhost for development.


### `[SECURITY]` No file type validation

Upload accepted any file, not just PDFs. Added validation for `.pdf` extension and `application/pdf` content type. I also added a restriction on the input in the frontend. Although it does not prevent a malicious user from sending a request in other ways (backend validation handles that), it helps well intentioned users select the right file.


### `[PERFORMANCE]` N+1 Query in `/documents`

Listing documents had an N+1 problem. One query for documents, then one query per document to get the processing status. Fixed using `joinedload(Document.processing_status)` to bring all data in a single query.


### `[BUG]` Files not deleted from disk

`DELETE /documents/{id}` only removed the database record, the file stayed on disk. Added `os.remove()` to delete the physical file.


### `[BUG]` No logging on database connection failure

Added try/catch with logging in `init_db()` so we know when the database can't be reached.


### `[INFRA]` Upload volume for easier debugging

Added a Docker volume mapping `./upload_data:/tmp/docproc_uploads` so uploaded files are visible on the host machine. This makes it easier to debug and verify uploads during development.


## Frontend

### `[BUG]` `window.location.reload()` anti-pattern

`UploadForm` was reloading the entire page after upload. Moved state up to `App` component and used a callback to refresh the document list without losing state.


### `[REFACTOR]` State lifted for tags

Moved tag filter state to `App` so it can be shared between `DocumentList` and `SearchBar`. This allowed the search to have access on this data and respect the selected tag filter.


## New Feature: Document Tagging

Implemented tagging feature:
- Users can add tags during upload
- Tags are always normalized to lowercase
- Documents can be filtered by tag in the list
- Clicking a tag on any document automatically selects it as the active filter
- Text search (searches within PDF content) also respects the selected tag filter
- Added a tag indicator in the search bar to show the active filter
- Created a `GET /tags` endpoint that returns all unique tags


## What I would do with more time

**Pagination for documents.** The list will grow and eventually become too slow to fetch everything at once. Pagination would fix this

**Async PDF processing.** Currently the PDF extraction blocks the event loop. I would run in an executor or use a background task queue

**Database migrations with Alembic.** Before implementing the tags feature, I would set up Alembic and create proper migrations. Then I would make the ALTER TABLE from the tags implementation just another migration.

**Edit tags.** Right now tags are set on upload only. I would suggest this possibility to understand if it makes sense for the user to update tags.

**AI tag suggestions.** Use an LLM API to suggest tags based on document content and previous tag assignments

**Better filter UX.** Create an advanced search that allows combining multiple tags for filtering and include and/or exclude keywords
