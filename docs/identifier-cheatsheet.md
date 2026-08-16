# Mobile Element Identifier Cheatsheet

## Recommended locator priority

1. Accessibility identifier / testID / content-description designed for testing and accessibility.
2. Visible text only when it is stable and product copy is unlikely to change.
3. Relative selectors such as `below`, `above`, `leftOf`, `rightOf`, or `childOf` when the UI is visually stable but identifiers are missing.
4. Coordinates only for tiny spikes or legacy screens while you negotiate proper identifiers.
5. XPath only as an Appium last resort.

## Maestro

```bash
maestro studio
maestro hierarchy
maestro test .maestro/flows/android/02_echo_message.yaml
maestro test --include-tags smoke .maestro/flows/android
```

Examples:

```yaml
- tapOn:
    id: "Login Screen"

- tapOn: "Save"

- scrollUntilVisible:
    element:
      id: "List Demo"
    direction: DOWN
```

## Appium

Use Appium Inspector to create a session, inspect the tree, then validate locators in your client language.

Examples:

```ts
await driver.$('~Login Screen').click();              // accessibility id
await driver.$('id:com.app:id/loginBtn').click();     // Android resource-id
await driver.$('-ios predicate string:name == "Login"').click();
```
