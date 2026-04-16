export default class __CLASS__ extends H5P.EventDispatcher {
  /**
   * @constructor
   *
   * @param {object} params Parameters passed by the editor.
   * @param {number} contentId Content's id.
   * @param {object} [extras] Saved state, metadata, etc.
   */
  constructor(params = {}, contentId, extras = {}) {
    super();

    const defaults = {
      textField: 'Hello %username'
    };

    this.params = { ...defaults, ...params };
    const username = (H5PIntegration && H5PIntegration.user && H5PIntegration.user.name) || 'world';

    this.element = document.createElement('div');
    this.element.className = 'h5p-__SLUG__';
    this.element.innerText = this.params.textField.replace('%username', username);
  }

  /**
   * Attach library to wrapper.
   *
   * @param {jQuery} $wrapper Content's container.
   */
  attach($wrapper) {
    $wrapper.get(0).appendChild(this.element);
  }
}
