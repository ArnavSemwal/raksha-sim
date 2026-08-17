---
name: High-Utility Medical Interface
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0edec'
  surface-container-high: '#ebe7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#434655'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#495c95'
  on-secondary: '#ffffff'
  secondary-container: '#acbfff'
  on-secondary-container: '#394c84'
  tertiary: '#943700'
  on-tertiary: '#ffffff'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#31447b'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '400'
    lineHeight: 30px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-xl:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  action-lg:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  touch-target-min: 64px
  screen-margin: 24px
  stack-gap: 16px
  section-gap: 40px
  button-padding-v: 24px
  button-padding-h: 32px
---

## Brand & Style

The design system is engineered for high-stress medical triage environments where speed of recognition and accuracy of interaction are the only metrics of success. The brand personality is clinical, urgent, and hyper-functional. 

The aesthetic is a variation of **Minimalism** blended with **Corporate/Modern** systematic rigor. By removing all non-essential decorative elements—including traditional navigation structures—the UI minimizes cognitive load. The emotional response is one of clarity and confidence, ensuring the practitioner remains focused on the patient rather than the interface.

## Colors

The palette is strictly functional. To prevent any confusion during emergency triage, **red, yellow, and green are strictly prohibited** from the core UI framework; these colors are reserved exclusively for dynamic medical status indicators (e.g., Triage Level 1-3).

- **Primary Action:** Cobalt Blue (#2563EB) is used for all "proceed" or "confirm" actions. It provides high contrast against the white background while remaining distinct from medical warning colors.
- **Primary Text:** Deep Charcoal (#121212) ensures maximum legibility and reduces eye strain under harsh hospital lighting.
- **Background:** Pure White (#FFFFFF) provides a sterile, high-contrast canvas.
- **Secondary Surfaces:** Soft Grays (#F8FAFC) are used only for grouping secondary information without adding visual weight.

## Typography

This design system utilizes **Inter** for its exceptional legibility and modern, systematic feel. The type scale is intentionally oversized to ensure readability from a distance or while in motion.

- **Headlines:** Bold and heavy weights are used to anchor each screen and provide immediate context.
- **Body:** Ample line height (1.5x) ensures that dense medical information remains digestible.
- **Action Labels:** Uses `action-lg` for buttons, ensuring the primary command is the most legible text on the screen.

## Layout & Spacing

The layout follows a **Fixed Single-Column Grid**. To eliminate distraction, there are no sidebars, hamburger menus, or tab bars. Every screen is a linear progression.

- **One Action Per Screen:** Layouts must center on a single primary decision point.
- **Safe Zones:** Generous 24px margins on all sides prevent accidental taps on hardware edges.
- **Vertical Rhythm:** A strict 8px baseline is used, with a default 40px gap between content sections to maintain visual separation.
- **Mobile First:** On mobile, components occupy the full width of the safe area to maximize tap surface.

## Elevation & Depth

This design system uses **Low-contrast outlines** and **Tonal layers** rather than shadows. Shadows are avoided to maintain a "flat" clinical look that doesn't distract from the data.

- **Level 0 (Base):** Pure White (#FFFFFF) background.
- **Level 1 (Interactive):** Elements have a 2px solid border in Deep Charcoal (#121212) or Cobalt Blue (#2563EB) to define tap boundaries.
- **Depth:** Content hierarchy is created through scale and color blocking rather than Z-axis elevation.

## Shapes

The shape language uses **Rounded** corners (0.5rem base) to provide a soft, approachable feel while maintaining the structural integrity of a professional tool.

- **Standard Buttons:** 0.5rem (8px) radius.
- **Large Container Cards:** 1rem (16px) radius to distinguish them from interactive buttons.
- **Inputs:** 0.5rem (8px) radius to match the button language.

## Components

### Buttons & Tap Targets
- **Primary Action:** Must be the full width of the screen (minus margins). Uses Cobalt Blue background with White text. Vertical padding is a minimum of 24px to create a massive hit area.
- **Secondary Action:** Ghost style with a 2px border in Deep Charcoal.

### Iconography
- All icons must be **Simple Outlines** (2px stroke width).
- Icons must always be accompanied by a text label. Never use an icon-only button.
- Icons are placed to the left of the text in buttons and list items.

### Inputs
- **Field Toggles:** Oversized radio-style buttons for binary or multiple-choice medical questions.
- **Text Fields:** Large 20px font size within the input, with a 2px border that thickens when focused.

### Triage Cards
- Used to display patient data summary.
- High contrast, 1px border. 
- No background color unless it is a system-reserved triage status color (managed outside this core UI spec).

### Progress Navigation
- A simple linear progress bar at the very top of the screen (4px height) indicates the depth of the current triage flow. No "back" button is present unless explicitly required for medical correction; the focus is forward momentum.