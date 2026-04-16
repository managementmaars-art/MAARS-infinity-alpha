# Web App Testing Examples

Comprehensive patterns for testing web applications with Chrome automation.

## Example 1: Form Validation Testing

**User request:**
"Test the signup form on localhost:3000. Try invalid email, missing password, and valid data."

**Complete workflow:**

```
1. Get tab context
tabs_context_mcp(createIfEmpty=true)
→ Returns: { tabId: 123, url: "about:blank", title: "" }

2. Navigate to app
navigate(url="http://localhost:3000/signup", tabId=123)
computer(action="wait", duration=2, tabId=123)

3. Take initial screenshot
computer(action="screenshot", tabId=123)

4. Test Case 1: Invalid email
form_input(ref="email", value="invalid-email", tabId=123)
form_input(ref="password", value="SecurePass123!", tabId=123)
computer(action="left_click", ref="submit-button", tabId=123)
computer(action="wait", duration=1, tabId=123)
get_page_text(tabId=123)
→ Check for: "Please enter a valid email address"

5. Clear form
navigate(url="http://localhost:3000/signup", tabId=123)
computer(action="wait", duration=1, tabId=123)

6. Test Case 2: Missing password
form_input(ref="email", value="test@example.com", tabId=123)
computer(action="left_click", ref="submit-button", tabId=123)
computer(action="wait", duration=1, tabId=123)
get_page_text(tabId=123)
→ Check for: "Password is required"

7. Clear form
navigate(url="http://localhost:3000/signup", tabId=123)
computer(action="wait", duration=1, tabId=123)

8. Test Case 3: Valid data
form_input(ref="email", value="test@example.com", tabId=123)
form_input(ref="password", value="SecurePass123!", tabId=123)
computer(action="left_click", ref="submit-button", tabId=123)
computer(action="wait", duration=2, tabId=123)

9. Check console for errors
read_console_messages(tabId=123, onlyErrors=true)
→ Should be empty

10. Check network for success
read_network_requests(tabId=123, urlPattern="/api/signup")
→ Check for: POST /api/signup → 201 Created

11. Verify success message
get_page_text(tabId=123)
→ Check for: "Account created successfully"

12. Report results
✅ Test Case 1: Invalid email → Error message displayed correctly
✅ Test Case 2: Missing password → Error message displayed correctly
✅ Test Case 3: Valid data → Signup successful, redirected to dashboard
✅ Console: No errors
✅ Network: POST /api/signup → 201 Created
```

**Expected outcome:**
```
✅ Signup Form Tested Successfully

Test Results:
1. Invalid email validation: PASS
   - Error message: "Please enter a valid email address"
2. Missing password validation: PASS
   - Error message: "Password is required"
3. Valid signup: PASS
   - Network: POST /api/signup → 201 Created
   - Redirect: /dashboard
   - Success message displayed

Console: 0 errors
Network: All requests successful

All validations passed!
```

## Example 2: User Flow Testing (Multi-Step)

**User request:**
"Test the complete checkout flow: add item to cart, go to checkout, fill shipping, submit order."

**Complete workflow:**

```
1. Get context
tabs_context_mcp(createIfEmpty=true)

2. Navigate to product page
navigate(url="http://localhost:3000/products/widget-pro", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

3. Add to cart
computer(action="left_click", ref="add-to-cart-button", tabId=<id>)
computer(action="wait", duration=1, tabId=<id>)
get_page_text(tabId=<id>)
→ Verify: "Item added to cart"

4. Go to cart
navigate(url="http://localhost:3000/cart", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)
get_page_text(tabId=<id>)
→ Verify: "Widget Pro" appears in cart

5. Proceed to checkout
computer(action="left_click", ref="checkout-button", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

6. Fill shipping information
form_input(ref="name", value="John Doe", tabId=<id>)
form_input(ref="address", value="123 Main St", tabId=<id>)
form_input(ref="city", value="San Francisco", tabId=<id>)
form_input(ref="zip", value="94102", tabId=<id>)

7. Take screenshot of filled form
computer(action="screenshot", tabId=<id>)

8. Submit order
computer(action="left_click", ref="place-order-button", tabId=<id>)
computer(action="wait", duration=3, tabId=<id>)

9. Check console for errors
read_console_messages(tabId=<id>, onlyErrors=true)

10. Check order submission network request
read_network_requests(tabId=<id>, urlPattern="/api/orders")
→ Verify: POST /api/orders → 200 OK

11. Verify confirmation page
get_page_text(tabId=<id>)
→ Check for: "Order confirmed" and order number

12. Take final screenshot
computer(action="screenshot", tabId=<id>)
```

**Expected outcome:**
```
✅ Checkout Flow Tested Successfully

Steps Completed:
1. Product page loaded → Widget Pro
2. Add to cart → Success message displayed
3. Cart page → Product appears in cart
4. Checkout page → Form loaded
5. Shipping info filled → All fields populated
6. Order submitted → POST /api/orders → 200 OK
7. Confirmation page → Order #12345 confirmed

Console: 0 errors
Network: All API calls successful
Total time: 15 seconds

Checkout flow working correctly!
```

## Example 3: API Integration Testing

**User request:**
"Test that the dashboard loads user data from the API correctly."

**Complete workflow:**

```
1. Get context
tabs_context_mcp(createIfEmpty=true)

2. Navigate to dashboard
navigate(url="http://localhost:3000/dashboard", tabId=<id>)
computer(action="wait", duration=3, tabId=<id>)

3. Monitor console during load
read_console_messages(tabId=<id>, onlyErrors=true)
→ Check: Should be empty

4. Check API requests
read_network_requests(tabId=<id>, urlPattern="/api/")
→ Expected requests:
   - GET /api/user/profile → 200 OK
   - GET /api/dashboard/stats → 200 OK
   - GET /api/dashboard/widgets → 200 OK

5. Verify request headers
read_network_requests(tabId=<id>, urlPattern="/api/user/profile")
→ Check Authorization header present:
   "Authorization: Bearer eyJ..."

6. Check response data
get_page_text(tabId=<id>)
→ Verify user data displayed:
   - Username
   - Email
   - Dashboard stats (numbers make sense)

7. Test data refresh
computer(action="left_click", ref="refresh-button", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

8. Verify refresh triggered new request
read_network_requests(tabId=<id>, urlPattern="/api/dashboard/stats")
→ Should have 2 requests (initial + refresh)

9. Check for any failed requests
read_network_requests(
  tabId=<id>,
  filterStatus=[400, 401, 403, 404, 500, 502, 503]
)
→ Should be empty

10. Report findings
```

**Expected outcome:**
```
✅ Dashboard API Integration Verified

API Calls:
1. GET /api/user/profile → 200 OK (520ms)
   - Headers: Authorization present ✓
   - Response: User data loaded ✓

2. GET /api/dashboard/stats → 200 OK (340ms)
   - Response: Stats displayed correctly ✓

3. GET /api/dashboard/widgets → 200 OK (890ms)
   - Response: 12 widgets rendered ✓

Refresh test:
- Triggered successfully ✓
- New API call made ✓
- Data updated on page ✓

Console: 0 errors
Network: 0 failed requests

API integration working correctly!
```

## Example 4: Visual Regression Testing

**User request:**
"I updated the header CSS. Compare before and after screenshots."

**Complete workflow:**

```
1. Get context
tabs_context_mcp(createIfEmpty=true)

2. Navigate to page
navigate(url="http://localhost:3000", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

3. Take "before" screenshot
computer(action="screenshot", tabId=<id>)
→ Saved as: screenshot-before.png

4. User makes CSS changes in code

5. Refresh page
navigate(url="http://localhost:3000", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

6. Take "after" screenshot
computer(action="screenshot", tabId=<id>)
→ Saved as: screenshot-after.png

7. Visual comparison
Assistant: "I've captured before and after screenshots. Here's what changed:

Before:
- Header height: ~80px
- Logo size: ~50px
- Navigation links: left-aligned

After:
- Header height: ~100px (increased)
- Logo size: ~60px (larger)
- Navigation links: centered
- Background color: white → light gray

The layout appears consistent across different viewport widths."

8. Test responsive behavior
browser_resize(width=768, height=1024, tabId=<id>)
computer(action="screenshot", tabId=<id>)
→ Check mobile view

9. Verify no console errors from CSS changes
read_console_messages(tabId=<id>, onlyErrors=true)
```

**Expected outcome:**
```
✅ Visual Changes Verified

Desktop View (1920x1080):
- Header height increased: 80px → 100px
- Logo scaled proportionally
- Navigation centered (was left-aligned)
- No layout breaks

Tablet View (768x1024):
- Responsive design maintained
- Mobile menu appears correctly

Console: 0 errors
No regressions detected

CSS changes applied successfully!
```

## Example 5: Error State Testing

**User request:**
"Test how the app handles a 500 error from the API."

**Complete workflow:**

```
1. Get context
tabs_context_mcp(createIfEmpty=true)

2. User configures mock server to return 500

3. Navigate to dashboard
navigate(url="http://localhost:3000/dashboard", tabId=<id>)
computer(action="wait", duration=3, tabId=<id>)

4. Check console for error handling
read_console_messages(tabId=<id>, onlyErrors=true)
→ Look for:
   - Caught error handling
   - User-friendly error message logged
   - No unhandled exceptions

5. Check network for 500 response
read_network_requests(
  tabId=<id>,
  urlPattern="/api/dashboard",
  filterStatus=[500]
)
→ Verify: GET /api/dashboard/stats → 500 Internal Server Error

6. Verify error UI displayed
get_page_text(tabId=<id>)
→ Check for error message:
   "Unable to load dashboard. Please try again later."

7. Test retry functionality
computer(action="left_click", ref="retry-button", tabId=<id>)
computer(action="wait", duration=2, tabId=<id>)

8. Verify retry made new request
read_network_requests(tabId=<id>, urlPattern="/api/dashboard")
→ Should show 2 requests (initial + retry)

9. Take screenshot of error state
computer(action="screenshot", tabId=<id>)

10. Report error handling quality
```

**Expected outcome:**
```
✅ Error Handling Verified

Error Scenario: API 500 Server Error

Console:
- ✓ Error caught gracefully
- ✓ User-friendly message logged
- ✓ No unhandled exceptions

Network:
- GET /api/dashboard/stats → 500 (as expected)
- Retry triggered second request

UI:
- ✓ Error message displayed to user
- ✓ Retry button available
- ✓ No blank/broken page state

Error handling implemented correctly!
```

## Example 6: Performance Testing

**User request:**
"Check if the dashboard loads within 3 seconds."

**Complete workflow:**

```
1. Get context
tabs_context_mcp(createIfEmpty=true)

2. Record start time
start_time = current_timestamp()

3. Navigate to dashboard
navigate(url="http://localhost:3000/dashboard", tabId=<id>)
computer(action="wait", duration=5, tabId=<id>)

4. Check network request timings
read_network_requests(tabId=<id>, urlPattern="/api/")
→ Analyze timing data:
   Request 1: GET /api/user/profile
   - DNS: 5ms
   - Connect: 12ms
   - Waiting (TTFB): 340ms
   - Receiving: 8ms
   - Total: 365ms

   Request 2: GET /api/dashboard/stats
   - Waiting: 890ms (SLOW)
   - Total: 910ms

   Request 3: GET /api/dashboard/widgets
   - Waiting: 1240ms (VERY SLOW)
   - Total: 1255ms

5. Calculate total load time
end_time = current_timestamp()
load_time = end_time - start_time
→ Total: 3.2 seconds (exceeds 3s target)

6. Identify bottlenecks
Bottlenecks found:
1. /api/dashboard/widgets (1.2s) - Largest contributor
2. /api/dashboard/stats (890ms) - Second largest

Recommendations:
- Add caching headers to /widgets endpoint
- Implement pagination for widgets (reduce payload)
- Consider lazy loading for below-fold widgets

7. Check if blocking resources
read_network_requests(tabId=<id>)
→ Look for large JS/CSS files:
   - bundle.js: 2.3MB (NOT gzipped) ← Problem
   - styles.css: 340KB

Additional recommendations:
- Enable gzip compression
- Code splitting for bundle.js
- Lazy load non-critical CSS

8. Report findings
```

**Expected outcome:**
```
⚠️ Performance Issues Detected

Load Time: 3.2 seconds (exceeds 3s target by 0.2s)

Slow API Requests:
1. GET /api/dashboard/widgets → 1240ms (SLOW)
   - Recommendation: Add caching, pagination
2. GET /api/dashboard/stats → 890ms
   - Recommendation: Add caching headers

Large Resources:
1. bundle.js → 2.3MB uncompressed
   - Recommendation: Enable gzip, code splitting
2. styles.css → 340KB
   - Recommendation: Lazy load non-critical CSS

Action Items:
1. Optimize /widgets API endpoint (highest impact)
2. Enable gzip compression (quick win)
3. Implement code splitting (medium effort)

Expected improvement: 3.2s → ~1.5s
```

## Common Testing Patterns

### Pattern: Test Form Validation

```
1. Navigate to form
2. For each validation rule:
   a. Enter invalid data
   b. Submit form
   c. Verify error message appears
3. Enter valid data
4. Submit form
5. Verify success
```

### Pattern: Test User Authentication

```
1. Navigate to login page
2. Enter invalid credentials
3. Verify error message
4. Enter valid credentials
5. Submit
6. Check for auth token in network request
7. Verify redirect to dashboard
8. Check console for errors
```

### Pattern: Test Responsive Design

```
1. Take screenshot at desktop size (1920x1080)
2. Resize to tablet (768x1024)
3. Take screenshot
4. Resize to mobile (375x667)
5. Take screenshot
6. Compare layouts
7. Verify no broken elements
```

### Pattern: Test CRUD Operations

```
1. Create: Fill form, submit, verify in list
2. Read: Navigate to list, verify item appears
3. Update: Click edit, modify data, save, verify changes
4. Delete: Click delete, confirm, verify removed from list
5. Check console and network for each operation
```

### Pattern: Test Error Recovery

```
1. Trigger error condition (network failure, 500 error)
2. Verify error message displayed
3. Check console for error handling
4. Test retry functionality
5. Verify app recovers gracefully
```
