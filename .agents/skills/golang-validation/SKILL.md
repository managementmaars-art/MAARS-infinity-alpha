---
name: golang-validation
description: "Go request validation with go-playground/validator/v10 — tag reference, custom validators, cross-field validation, dive for collections, error humanization, httpin integration. Use when adding validation to Go structs, writing custom validators, or handling validation errors in HTTP APIs."
metadata:
  author: openserbia
  version: "1.0.0"
---

# Go Validation with go-playground/validator

Comprehensive guide for struct validation in Go HTTP services using `go-playground/validator/v10` integrated with `httpin` for request binding.

## Setup — Do Once

```go
var validate = validator.New()

func init() {
// Use JSON tag names in error messages, not Go struct field names
validate.RegisterTagNameFunc(func (fld reflect.StructField) string {
tag := fld.Tag.Get("json")
if tag == "-" || tag == "" {
return fld.Name
}
if i := strings.Index(tag, ","); i != -1 {
return tag[:i]
}
return tag
})

// Register all custom validators here
}
```

### Rules

- **Singleton instance** — create ONE validator at package level, reuse everywhere. The validator caches struct metadata after first validation; creating new instances loses the cache.
- **Register at startup** — all custom validators and struct validators MUST be registered during `init()`. Registration is NOT thread-safe.
- **Use `validate.StructCtx`** — always pass context for cancellation support.

```go
// Bad — new instance per call, no caching
func handler(w http.ResponseWriter, r *http.Request) {
v := validator.New()
v.Struct(req)
}

// Good — singleton, cached
func handler(w http.ResponseWriter, r *http.Request) {
validate.StructCtx(r.Context(), req)
}
```

## Tag Reference

### Requirement Tags

| Tag | Purpose | Example |
| --- | --- | --- |
| `required` | Must not be zero value | `validate:"required"` |
| `omitempty` | Skip if empty, validate if present | `validate:"omitempty,gt=0"` |
| `required_if=Field value` | Required when another field equals value | `validate:"required_if=Type offline"` |
| `required_unless=Field value` | Required unless another field equals value | `validate:"required_unless=Status draft"` |
| `required_with=Field` | Required if another field is present | `validate:"required_with=EndDate"` |
| `required_with_all=F1 F2` | Required if ALL listed fields present | `validate:"required_with_all=StartDate EndDate"` |
| `required_without=Field` | Required if another field is absent | `validate:"required_without=Email"` |
| `excluded_if=Field value` | Excluded when condition met | `validate:"excluded_if=Type internal"` |

### Numeric Comparisons

| Tag     | Purpose                                                          | Example              |
| ------- | ---------------------------------------------------------------- | -------------------- |
| `gt=N`  | Greater than                                                     | `validate:"gt=0"`    |
| `gte=N` | Greater than or equal                                            | `validate:"gte=1"`   |
| `lt=N`  | Less than                                                        | `validate:"lt=100"`  |
| `lte=N` | Less than or equal                                               | `validate:"lte=365"` |
| `eq=N`  | Equals                                                           | `validate:"eq=10"`   |
| `ne=N`  | Not equals                                                       | `validate:"ne=0"`    |
| `min=N` | Minimum (length for strings, size for slices, value for numbers) | `validate:"min=1"`   |
| `max=N` | Maximum                                                          | `validate:"max=100"` |
| `len=N` | Exact length/value                                               | `validate:"len=5"`   |

### Cross-Field Comparisons

| Tag                | Purpose                              | Example                             |
| ------------------ | ------------------------------------ | ----------------------------------- |
| `eqfield=Field`    | Equals another field                 | `validate:"eqfield=Password"`       |
| `nefield=Field`    | Not equals another field             | `validate:"nefield=OldEmail"`       |
| `gtfield=Field`    | Greater than another field           | `validate:"gtfield=StartDate"`      |
| `gtefield=Field`   | Greater than or equal                | `validate:"gtefield=MinPrice"`      |
| `gtecsfield=Field` | Greater than or equal (cross-struct) | `validate:"gtecsfield=RequestedAt"` |
| `ltfield=Field`    | Less than another field              | `validate:"ltfield=MaxPrice"`       |
| `ltefield=Field`   | Less than or equal                   | `validate:"ltefield=EndDate"`       |

### String Validators

| Tag                    | Purpose                                |
| ---------------------- | -------------------------------------- |
| `email`                | Valid email                            |
| `url`                  | Valid URL                              |
| `uri`                  | Valid URI                              |
| `uuid` / `uuid4`       | UUID format                            |
| `alpha`                | Letters only                           |
| `numeric`              | Digits only                            |
| `alphanumeric`         | Letters and digits                     |
| `contains=sub`         | Contains substring                     |
| `startswith=pre`       | Starts with prefix                     |
| `endswith=suf`         | Ends with suffix                       |
| `oneof=a b c`          | One of listed values (space-separated) |
| `ip` / `ipv4` / `ipv6` | IP address                             |
| `json`                 | Valid JSON string                      |
| `base64`               | Base64 encoded                         |

### Collection Tags

| Tag                | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `dive`             | Validate each element in slice/array/map         |
| `keys` / `endkeys` | Validate map keys (between `keys` and `endkeys`) |

## Good vs Bad Examples

### Required vs Omitempty

```go
// Bad — always validates even when field not provided
type Filter struct {
MinPrice int `validate:"gt=0"`
}
// If MinPrice is 0 (not set), validation FAILS

// Good — only validates if present
type Filter struct {
MinPrice *int `validate:"omitempty,gt=0"`
}
// If MinPrice is nil, validation PASSES. If set to -1, FAILS.
```

### Enum Values with oneof

```go
// Bad — magic strings, easy to get wrong
type Request struct {
Status string `validate:"required"`
}

// Good — restricted to known values
type Request struct {
Status string `validate:"required,oneof=active inactive suspended"`
}
```

### Conditional Required Fields

```go
// Bad — card number always required
type Payment struct {
Method     string `validate:"required,oneof=card bank"`
CardNumber string `validate:"required"`
}

// Good — card number only required for card payments
type Payment struct {
Method     string `validate:"required,oneof=card bank"`
CardNumber string `validate:"required_if=Method card"`
BankCode   string `validate:"required_if=Method bank"`
}
```

### Date Ordering with Cross-Field Validation

```go
// Bad — no ordering enforcement
type DateRange struct {
StartDate string `validate:"required,mustdate"`
EndDate   string `validate:"required,mustdate"`
}

// Good — end must be >= start
type DateRange struct {
StartDate string `validate:"required,mustdate"`
EndDate   string `validate:"required,mustdate,gtecsfield=StartDate"`
}
```

### Chained Date Fields

For multi-step processes where dates must be in chronological order:

```go
type ResidenceApplication struct {
RequestedAt  string `validate:"required_if=Type offline,omitempty,mustdate,date_limit"`
AppointedAt  string `validate:"omitempty,mustdate,date_limit,gtecsfield=RequestedAt"`
AppliedAt    string `validate:"omitempty,mustdate,date_limit,gtecsfield=AppointedAt"`
BiometryAt   string `validate:"omitempty,mustdate,date_limit,gtecsfield=AppliedAt"`
IssuedAt     string `validate:"omitempty,mustdate,date_limit,gtecsfield=BiometryAt"`
}
```

Each date must be >= the previous one when set. `omitempty` allows skipping intermediate steps.

### Slice/Array Validation with dive

```go
// Bad — validates slice length, not contents
type Request struct {
Tags []string `validate:"required,min=1"`
}
// ["", "", ""] passes — 3 empty strings!

// Good — validates each element
type Request struct {
Tags []string `validate:"required,gt=0,dive,required,min=2,max=50"`
}
// Slice must have >0 items, each item 2-50 chars, none empty

// Good — validate message IDs
type DeleteRequest struct {
MessageIDs []int64 `validate:"required,min=1,max=1000,dive,gt=0"`
}
// 1-1000 IDs, each must be positive
```

### Map Validation with keys/endkeys

```go
// Good — validate both keys and values
type Config struct {
Headers map[string]string `validate:"dive,keys,required,min=1,endkeys,required"`
}
```

### Nested Structs with dive

```go
type Team struct {
Members []Member `validate:"required,dive"`
}

type Member struct {
Name  string `validate:"required,min=2"`
Email string `validate:"required,email"`
}
// Each member is validated with its own rules
```

### Pointer Fields for Optional Parameters

```go
// Bad — zero value is ambiguous (is 0 "not set" or "set to zero"?)
type Filter struct {
UserID    int64  `validate:"omitempty,gt=0"`
ChannelID int64  `validate:"omitempty,gt=0"`
}

// Good — nil means "not provided", non-nil means "validate it"
type Filter struct {
UserID    *int64 `validate:"omitempty,gt=0"`
ChannelID *int64 `validate:"omitempty,gt=0"`
}
```

## Custom Validators

### Pattern — Domain Enum Validator

Validate against a defined set of domain constants:

```go
_ = validate.RegisterValidation("eventtype", func (fl validator.FieldLevel) bool {
if fl.Field().IsZero() {
return true // let omitempty handle empty values
}
v, ok := fl.Field().Interface().(string)
if !ok {
return false
}
for _, t := range domain.AllEventTypes {
if v == t.String() {
return true
}
}
return false
})
```

Use: `validate:"required,eventtype"`

**Why custom over `oneof`:** The list of valid values comes from domain code, not hardcoded in a tag. Adding a new enum value doesn't require updating every struct tag.

### Pattern — Date Format Validator

```go
_ = validate.RegisterValidation("mustdate", func (fl validator.FieldLevel) bool {
v, ok := fl.Field().Interface().(string)
if !ok {
return false
}
_, err := time.Parse("2006-01-02", v)
return err == nil
})
```

Use: `validate:"required,mustdate"`

### Pattern — Date Range Validator

```go
_ = validate.RegisterValidation("date_limit", func (fl validator.FieldLevel) bool {
v, ok := fl.Field().Interface().(string)
if !ok {
return false
}
t, err := time.Parse("2006-01-02", v)
if err != nil {
return true // let mustdate handle format errors
}
now := time.Now()
return !t.Before(now.AddDate(-5, 0, 0)) && !t.After(now.AddDate(5, 0, 0))
})
```

Use: `validate:"mustdate,date_limit"` — always pair with `mustdate` so format is checked first.

### Rules for Custom Validators

- Return `true` for zero values if the validator should have omitempty-like behavior
- Let other validators handle concerns that aren't yours (format vs range)
- Keep validators pure — no database calls, no I/O. Use struct-level validation or service-layer validation for those.

```go
// Bad — database call in validator, tight coupling
_ = validate.RegisterValidation("userExists", func (fl validator.FieldLevel) bool {
return database.UserExists(fl.Field().Int()) // DON'T DO THIS
})

// Good — validate format/range only, check existence in service layer
_ = validate.RegisterValidation("validUserID", func (fl validator.FieldLevel) bool {
return fl.Field().Int() > 0
})
```

## Two-Layer Validation

Use **tag-based validation** for field-level constraints and **service-layer validation** for complex business rules that cross multiple fields or require external data.

### Layer 1 — Tag-Based (in handler)

```go
func (h *Handler) create(w http.ResponseWriter, r *http.Request) {
req := r.Context().Value(httpin.Input).(*CreateRequest)

if err := validate.StructCtx(r.Context(), req); err != nil {
httpx.WriteValidationError(w, r, err)
return
}

// Layer 2 happens next...
}
```

### Layer 2 — Domain Logic (in service)

For rules that can't be expressed with tags — cross-field business logic, conditional requirements based on data combinations:

```go
func ValidateApplication(req *domain.Application) *httpx.ValidationErrors {
var errs []httpx.ValidationError

// Business rule: Belgrade requires appointment for offline applications
if req.City == "Belgrade" && req.Type == "offline" && req.AppointmentAt == "" {
errs = append(errs, httpx.ValidationError{
Path:    "appointment_at",
Message: "appointment is required for Belgrade offline applications",
})
}

if len(errs) > 0 {
return &httpx.ValidationErrors{Fields: errs}
}
return nil
}
```

### Handler with Both Layers

```go
func (h *Handler) create(w http.ResponseWriter, r *http.Request) {
req := r.Context().Value(httpin.Input).(*CreateRequest)

// Layer 1: field constraints
if err := validate.StructCtx(r.Context(), req); err != nil {
httpx.WriteValidationError(w, r, err)
return
}

d := req.ToDomain()

// Layer 2: business rules
if verrs := service.ValidateApplication(d); verrs != nil {
httpx.WriteError(w, r, http.StatusBadRequest, httpx.CodeValidation,
"validation failed", map[string]any{"fields": verrs.Fields})
return
}

// All validation passed — proceed
if err := h.svc.Create(r.Context(), d); err != nil {
// ...
}
}
```

## Error Humanization

Transform validator errors into API-friendly messages:

```go
type ValidationError struct {
Path    string `json:"path"`
Message string `json:"message"`
}

type ValidationErrors struct {
Fields []ValidationError `json:"fields"`
}

func TransformValidationErrors(verrs validator.ValidationErrors) *ValidationErrors {
fields := &ValidationErrors{
Fields: make([]ValidationError, 0, len(verrs)),
}
for _, fe := range verrs {
fields.Fields = append(fields.Fields, ValidationError{
Path:    fe.Field(),
Message: humanizeTag(fe.Tag(), fe),
})
}
return fields
}

func humanizeTag(tag string, fe validator.FieldError) string {
switch tag {
case "required":
return "is required"
case "gt":
if fe.Param() != "" {
return "must be greater than " + fe.Param()
}
return "must be greater than 0"
case "gte":
if fe.Param() != "" {
return "must be greater than or equal to " + fe.Param()
}
return "must be greater than or equal to 0"
case "gtecsfield":
return "must be greater than or equal to " + fe.Param()
case "lt":
if fe.Param() != "" {
return "must be less than " + fe.Param()
}
return "must be less than the limit"
case "lte":
if fe.Param() != "" {
return "must be less than or equal to " + fe.Param()
}
return "must be less than or equal to the limit"
case "min":
if fe.Param() != "" {
return "is too short (min " + fe.Param() + ")"
}
return "is too short"
case "max":
if fe.Param() != "" {
return "is too long (max " + fe.Param() + ")"
}
return "is too long"
case "oneof":
return "must be one of " + fe.Param()
case "required_if":
return "required if " + fe.Param()
case "required_with":
return "required when " + fe.Param() + " is set"
case "email":
return "must be a valid email"
case "url":
return "must be a valid URL"
case "uuid4":
return "must be a valid UUID"
case "dive":
return "contains invalid item(s)"
default:
return "invalid"
}
}
```

**Always extend `humanizeTag` when adding custom validators** — don't let them fall through to "invalid".

## Integration with httpin

httpin handles request parsing, validator handles field validation. They work on the same struct:

```go
type ListItemsRequest struct {
Status  *string `in:"query=status" json:"status" validate:"omitempty,oneof=active inactive"`
Type    *string `in:"query=type" json:"type" validate:"omitempty,oneof=online offline"`
httpx.PaginationParams
}

func (h *Handler) Register(r chi.Router) {
r.With(httpin.NewInput(ListItemsRequest{})).Get("/items", h.list)
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) {
req := r.Context().Value(httpin.Input).(*ListItemsRequest)

if err := validate.StructCtx(r.Context(), req); err != nil {
httpx.WriteValidationError(w, r, err)
return
}
// ...
}
```

### Tag mapping

| Source      | httpin tag                    | Validator tag                                |
| ----------- | ----------------------------- | -------------------------------------------- |
| Query param | `in:"query=status"`           | `validate:"omitempty,oneof=active inactive"` |
| Path param  | `in:"path=id"`                | `validate:"required,gt=0"`                   |
| JSON body   | `in:"body=json"`              | `validate:"required"` (on payload field)     |
| Form field  | `in:"form=name"`              | `validate:"required,min=1,max=255"`          |
| Header      | `in:"header=X-Token"`         | `validate:"required"`                        |
| Default     | `in:"query=limit;default=20"` | `validate:"min=1,max=100"`                   |

## Common Mistakes

| Mistake                                          | Fix                                                             |
| ------------------------------------------------ | --------------------------------------------------------------- |
| Creating validator per request                   | Use singleton `var validate = validator.New()`                  |
| Registering validators during requests           | Register in `init()` only                                       |
| Missing `omitempty` on optional fields           | Add `omitempty` before other tags                               |
| Using `int` for optional numerics                | Use `*int` with `omitempty`                                     |
| `min=1` on slice without `dive`                  | Add `dive` to validate elements                                 |
| Typo in cross-field reference `eqfield=Passwrod` | Double-check field names — typos silently pass                  |
| Database calls in custom validators              | Keep validators pure; use service-layer validation              |
| Complex business rules in tags                   | Use two-layer validation — tags for constraints, code for logic |
| Not humanizing custom validator errors           | Extend `humanizeTag` for every custom tag                       |
| Same struct for DB entity and request DTO        | Separate: domain entities for persistence, DTOs for transport   |
| `validate:"required"` on body payload pointer    | Validate the inner fields, not the pointer itself               |
| Missing `RegisterTagNameFunc`                    | Always register — errors should show `user_id` not `UserID`     |

## API Error Response

Validation errors return 400 with the unified error envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "validation failed",
    "details": {
      "fields": [
        {
          "path": "name",
          "message": "is required"
        },
        {
          "path": "type",
          "message": "must be one of online offline"
        },
        {
          "path": "applied_at",
          "message": "must be greater than or equal to requested_at"
        }
      ]
    }
  },
  "request_id": "abc-123",
  "timestamp": "2025-01-01T00:00:00Z"
}
```
