# Phase 12: UI Fixes Round 2

## Issues from Phase 11 Review

### FIX-01: Ghost cards too dark
The greyed-out "not found" items (cards with no listings) are too dark to read. Current opacity 0.35 needs increasing.

### FIX-02: Inconsistent price sizing
Price display varies in size depending on whether it's a deal or not. Should be consistent regardless of deal status.

### FIX-03: Font overhaul
All fonts (except the logo wordmark) need to be changed. Current font choices don't work for body/UI text.

### FIX-04: Email template missing logo and font
The deal alert email still doesn't have the logo included and the title font is incorrect.

### FIX-05: Deal alerts sent when notify not checked
Deal alert emails are being sent even when the notify button/checkbox is not checked. This is a functional bug.

### FIX-06: Remove tick icon (bottom right)
There's a tick icon in the bottom right corner with no clear purpose. Remove it.

### FIX-07: Scrollbar not applied
The custom scrollbar styling from the design spec has not been visually applied.

### FIX-08: Card titles too small
Card titles on the dashboard should be larger for better readability.
