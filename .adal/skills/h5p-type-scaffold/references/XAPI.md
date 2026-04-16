# xAPI Integration

H5P content types emit xAPI statements through the built-in event system. Platforms are responsible for forwarding those statements to an LRS.

## Emitting Statements (Content Type)

Use the EventDispatcher helpers available on content type instances:

```js
// Example: scored/answered statement
this.triggerXAPIScored(score, maxScore, 'answered', true, success);

// Example: generic verb
this.triggerXAPI('attempted');
```

`triggerXAPIScored` and `triggerXAPI` are part of the EventDispatcher API.

## Listening to Statements

xAPI statements are emitted as events:

```js
// Listen on the instance
instance.on('xAPI', function (event) {
  console.log(event.data.statement);
});

// Or listen globally
H5P.externalDispatcher.on('xAPI', function (event) {
  console.log(event.data.statement);
});
```

## Platform Responsibilities

H5P does not include its own LRS integration. The publishing platform is expected to forward xAPI statements to an LRS.

### Drupal

- **H5P Analytics** captures H5P xAPI statements and forwards them to an LRS.
- **LMS H5P** (with LMS XAPI) also forwards statements and supports scoring.

### Lumi Education (H5P NodeJS Library)

If you use `@lumieducation/h5p-webcomponents`, the H5P player emits an `xAPI` event that includes:

- `event.detail.statement`
- `event.detail.context`
- `event.detail.event`

Your host should listen for that event and forward statements to an LRS.

## Checklist

- Emit xAPI statements from the content type when key actions occur.
- Verify statements fire in the browser via `instance.on('xAPI', ...)`.
- Ensure your platform captures and forwards statements to an LRS.

## References
- https://h5p.org/documentation/x-api
- https://h5p.org/events
- https://h5p.org/documentation/api/H5P.EventDispatcher.html
- https://h5p.org/node/3391
- https://docs.lumi.education/npm-packages/h5p-webcomponents
- https://www.drupal.org/project/h5p_analytics
- https://www.drupal.org/project/lms_h5p
