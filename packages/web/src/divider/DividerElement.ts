import { css, CSSResultGroup, html, LitElement } from "lit";
import { property } from "lit/decorators.js";

import { customElement, DesignToken, Role } from "m3e/core";

/** viewBox 宽度，配合 preserveAspectRatio="none" 横向拉满 */
const WAVE_WIDTH = 1200;
/** 波幅（viewBox 单位，会随元素高度纵向缩放） */
const WAVE_AMPLITUDE = 3;
/** 波长（viewBox 单位） */
const WAVE_WAVELENGTH = 80;
const WAVE_HEIGHT = WAVE_AMPLITUDE * 2 + 2;
let WAVE_PATH = `M0 ${WAVE_HEIGHT / 2}`;
for (let x = 2; x <= WAVE_WIDTH; x += 2) {
  WAVE_PATH += ` L${x} ${(WAVE_HEIGHT / 2 + WAVE_AMPLITUDE * Math.sin((x / WAVE_WAVELENGTH) * Math.PI * 2)).toFixed(2)}`;
}

/**
 * A thin line that separates content in lists or other containers.
 *
 * @description
 * The `m3e-divider` component visually separates content within layouts, lists, or containers using a thin, unobtrusive line.
 * It supports horizontal and vertical orientation, with optional inset variants to align with layout padding and visual hierarchy.
 * The divider thickness, color, and inset behavior are customizable via CSS properties to maintain consistency across surfaces.
 * It is designed to reinforce spatial relationships without drawing attention, preserving focus on primary content.
 *
 * @example
 * The following example illustrates a basic horizontal divider.
 * ```html
 * <m3e-divider></m3e-divider>
 * ```
 *
 * @tag m3e-divider
 *
 * @attr variant - The appearance of the divider: `solid` (default) or `wavy`.
 * @attr inset - Whether the divider is indented with equal padding on both sides.
 * @attr inset-start - Whether the divider is indented with padding on the leading side.
 * @attr inset-end - Whether the divider is indented with padding on the trailing side.
 * @attr vertical - Whether the divider is vertically aligned with adjacent content.
 *
 * @cssprop --m3e-divider-thickness - Thickness of the divider line.
 * @cssprop --m3e-divider-color - Color of the divider line.
 * @cssprop --m3e-divider-wavy-amplitude - Amplitude of the `wavy` variant.
 * @cssprop --m3e-divider-wavy-height - Height of the `wavy` variant.
 * @cssprop --m3e-divider-inset-size - When inset, fallback inset size used when no specific start or end inset is provided.
 * @cssprop --m3e-divider-inset-start-size - When inset, leading inset size.
 * @cssprop --m3e-divider-inset-end-size - When inset, trailing inset size.
 */
@customElement("m3e-divider")
export class M3eDividerElement extends Role(LitElement, "separator") {
  /** The styles of the element. */
  static override styles: CSSResultGroup = css`
    :host {
      display: block;
      position: relative;
    }
    :host([hidden]) {
      display: none;
    }
    :host(:not([vertical])) {
      height: var(--m3e-divider-thickness, 1px);
      width: 100%;
    }
    :host([vertical]) {
      width: var(--m3e-divider-thickness, 1px);
      height: 100%;
    }
    .line {
      contain: layout style paint;
      box-sizing: border-box;
      position: absolute;
    }
    :host(:not([vertical])) .line {
      border-bottom: var(--m3e-divider-thickness, 1px) solid
        var(--m3e-divider-color, ${DesignToken.color.outlineVariant});
      height: inherit;
    }
    :host([vertical]) .line {
      border-right: var(--m3e-divider-thickness, 1px) solid
        var(--m3e-divider-color, ${DesignToken.color.outlineVariant});
      width: inherit;
    }
    :host([vertical][inset]) .line,
    :host([vertical][inset-start]) .line {
      top: var(--m3e-divider-inset-start-size, var(--m3e-divider-inset-size, ${DesignToken.measurement.space200}));
    }
    :host(:not([vertical])[inset]) .line,
    :host(:not([vertical])[inset-start]) .line {
      left: var(--m3e-divider-inset-start-size, var(--m3e-divider-inset-size, ${DesignToken.measurement.space200}));
    }
    :host([vertical][inset]) .line,
    :host([vertical][inset-end]) .line {
      bottom: var(--m3e-divider-inset-end-size, var(--m3e-divider-inset-size, ${DesignToken.measurement.space200}));
    }
    :host(:not([vertical])[inset]) .line,
    :host(:not([vertical])[inset-end]) .line {
      right: var(--m3e-divider-inset-end-size, var(--m3e-divider-inset-size, ${DesignToken.measurement.space200}));
    }
    :host([vertical]:not([inset]):not([inset-start])) .line {
      top: 0;
    }
    :host(:not([vertical]):not([inset]):not([inset-start])) .line {
      left: 0;
    }
    :host([vertical]:not([inset]):not([inset-end])) .line {
      bottom: 0;
    }
    :host(:not([vertical]):not([inset]):not([inset-end])) .line {
      right: 0;
    }
    :host([variant="wavy"]:not([vertical])) {
      height: var(
        --m3e-divider-wavy-height,
        calc(var(--m3e-divider-thickness, 2px) + 2 * var(--m3e-divider-wavy-amplitude, 3px))
      );
    }
    :host([variant="wavy"]:not([vertical])) .wave {
      display: block;
      width: 100%;
      height: 100%;
    }
    :host([variant="wavy"]:not([vertical])) .wave path {
      fill: none;
      stroke: var(--m3e-divider-color, ${DesignToken.color.outlineVariant});
      stroke-width: var(--m3e-divider-thickness, 2px);
    }
    @media (forced-colors: active) {
      .line {
        border-color: GrayText;
      }
      :host([variant="wavy"]:not([vertical])) .wave path {
        stroke: GrayText;
      }
    }
  `;

  /**
   * The appearance of the divider.
   * @default "solid"
   */
  @property({ reflect: true }) variant: "solid" | "wavy" = "solid";

  /**
   * Whether the divider is vertically aligned with adjacent content.
   * @default false
   */
  @property({ type: Boolean, reflect: true }) vertical = false;

  /**
   * Whether the divider is indented with equal padding on both sides.
   * @default false
   */
  @property({ type: Boolean, reflect: true }) inset = false;

  /**
   * Whether the divider is indented with padding on the leading side.
   * @default false
   */
  @property({ attribute: "inset-start", type: Boolean, reflect: true }) insetStart = false;

  /**
   * Whether the divider is indented with padding on the trailing side.
   * @default false
   */
  @property({ attribute: "inset-end", type: Boolean, reflect: true }) insetEnd = false;

  /** @inheritdoc */
  protected override render(): unknown {
    if (this.variant === "wavy" && !this.vertical) {
      return html`<svg class="wave" viewBox="0 0 ${WAVE_WIDTH} ${WAVE_HEIGHT}" preserveAspectRatio="none" aria-hidden="true">
        <path d=${WAVE_PATH} vector-effect="non-scaling-stroke"></path>
      </svg>`;
    }
    return html`<div class="line"></div>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "m3e-divider": M3eDividerElement;
  }
}
