import { extend } from '@services/util.js';
import { getSemanticsDefaults } from '@services/util-h5p.js';
import Dictionary from '@services/dictionary.js';
import '@styles/h5p-__SLUG__.css';

/** @constant {string} Default description */
const DEFAULT_DESCRIPTION = '__TITLE__';

export default class __CLASS__ extends H5P.EventDispatcher {
  /**
   * @class
   * @param {object} params Parameters passed by the editor.
   * @param {number} contentId Content's id.
   * @param {object} [extras] Saved state, metadata, etc.
   */
  constructor(params, contentId, extras = {}) {
    super();

    const defaults = extend({}, getSemanticsDefaults());
    this.params = extend(defaults, params);

    this.contentId = contentId;
    this.extras = extras;

    this.dictionary = new Dictionary();
    this.dictionary.fill({ l10n: this.params.l10n, a11y: this.params.a11y });

    this.previousState = this.extras.previousState || {};

    this.dom = this.buildDOM();
  }

  /**
   * Attach library to wrapper.
   * @param {H5P.jQuery} $wrapper Content's container.
   */
  attach($wrapper) {
    const wrapper = $wrapper.get(0);
    wrapper.classList.add('h5p-__SLUG__');
    wrapper.appendChild(this.dom);
  }

  /**
   * Build main DOM.
   * @returns {HTMLElement} Main DOM.
   */
  buildDOM() {
    const dom = document.createElement('div');
    dom.classList.add('h5p-__SLUG__-main');
    dom.textContent = this.getTitle();

    return dom;
  }

  /**
   * Get task title.
   * @returns {string} Title.
   */
  getTitle() {
    return H5P.createTitle(this.extras?.metadata?.title || DEFAULT_DESCRIPTION);
  }

  /**
   * Get description.
   * @returns {string} Description.
   */
  getDescription() {
    return DEFAULT_DESCRIPTION;
  }
}
