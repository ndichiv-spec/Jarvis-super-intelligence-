# Accessibility Guide

## Compliance Target

JARVIS Home targets **WCAG 2.2 Level AA** compliance.

## Keyboard Navigation

- All interactive elements are reachable via Tab
- Command Palette: `Cmd+K` / `Ctrl+K`
- Sidebar collapse: accessible via toggle button
- All dropdowns support arrow key navigation
- Escape closes modals, dropdowns, and command palette
- Enter/Space activates focused elements

## Focus Management

- Visible focus indicators on all interactive elements
- Focus ring uses `ring` CSS variable for theme consistency
- Skip-to-content link pattern for keyboard users
- Focus trapped in modals and command palette
- Focus returns to trigger element when closing overlays

## ARIA

- Landmark regions: `<nav>`, `<main>`, `<header>`, `<aside>`
- ARIA labels on icon-only buttons
- `role="navigation"` on sidebar
- `role="search"` on search inputs
- `aria-expanded` on collapsible elements
- `aria-current="page"` on active nav items
- `aria-live="polite"` on dynamic content regions

## Screen Reader Support

- All icons have accessible labels via `aria-label` or `sr-only` text
- Status dots include text labels
- Loading states are announced
- Error states are announced
- Notifications include descriptive text

## Color and Contrast

- All text meets 4.5:1 contrast ratio (AA)
- Large text meets 3:1 contrast ratio
- Status colors remain distinguishable in both themes
- Focus indicators have 3:1 contrast against backgrounds
- Color is never the sole indicator of meaning

## Reduced Motion

- `prefers-reduced-motion` respected
- Framer Motion animations disabled when reduced motion preferred
- Essential animations only (loading indicators, status changes)
- No parallax or continuous animations

## Testing

- Manual keyboard navigation audit
- Automated axe-core checks in CI
- Color contrast verification
- Screen reader testing with NVDA and VoiceOver
- Zoom testing up to 200%
