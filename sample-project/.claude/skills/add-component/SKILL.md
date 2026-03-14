---
name: add-component
description: Create a new React component with proper structure, props interface, styling, and tests.
user-invokable: true
argument-hint: "ComponentName"
---

# Add a New React Component

Creating component: `$ARGUMENTS`

## Step 1: Component File

Create `frontend/src/components/$ARGUMENTS/$ARGUMENTS.tsx`:

```typescript
import { forwardRef } from 'react'

interface $ARGUMENTSProps {
  // Define props here
}

export const $ARGUMENTS = forwardRef<HTMLDivElement, $ARGUMENTSProps>(
  function $ARGUMENTS(props, ref) {
    return (
      <div ref={ref} className="...">
        {/* Component content */}
      </div>
    )
  }
)
```

### Conventions
- `PascalCase` file and component name
- `forwardRef` if parent may need scroll-to-view
- Props interface named `{Component}Props`
- Export as named export (not default)

## Step 2: Styling

Use Tailwind utility classes directly. For shared design tokens, reference `app.css`:

```typescript
// Use semantic token classes
<div className="bg-bg-card text-text-primary rounded-lg p-4">
```

- No CSS modules or inline styles
- No hardcoded hex colors — use semantic tokens
- Dark theme by default

## Step 3: Test File

Create `frontend/src/components/$ARGUMENTS/$ARGUMENTS.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { $ARGUMENTS } from './$ARGUMENTS'

// Test factory
function make$ARGUMENTS(overrides: Partial<$ARGUMENTSProps> = {}) {
  return { /* default props */, ...overrides }
}

describe('$ARGUMENTS', () => {
  it('renders without crashing', () => {
    render(<$ARGUMENTS {...make$ARGUMENTS()} />)
    // assertions
  })

  it('handles empty state', () => {
    render(<$ARGUMENTS {...make$ARGUMENTS({ items: [] })} />)
    expect(screen.getByText(/no items/i)).toBeInTheDocument()
  })
})
```

## Step 4: Export

Add to barrel export if one exists:
```typescript
// frontend/src/components/index.ts
export { $ARGUMENTS } from './$ARGUMENTS/$ARGUMENTS'
```

## Verify

```bash
cd frontend && npx tsc --noEmit && npx vitest run
```
