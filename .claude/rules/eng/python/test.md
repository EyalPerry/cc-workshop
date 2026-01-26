---
path: {src,test,tests}/**/*.py
---

## Test Suite

### Flat Modules
Use flat modules with functions. Usage of classes for grouping tests is **UNACCEPTABLE**.

**Pattern (Good)**: Separate test suites into individual files based on functionality.
```python
# file: test_todo_creation.py
def test_should_create_todo_with_default_status():
    ...
# file: test_todo_completion.py
def test_should_mark_todo_as_completed_when_done():
    ...
```
**Anti-Pattern (Bad)**: Grouping tests in classes within a single file.
```python
class TestTodoCreation:
    def test_should_create_todo_with_default_status(self):
        ...
class TestTodoCompletion:
    def test_should_mark_todo_as_completed_when_done(self):
        ...
```

### Utility Scoping
Place utility classes and models relevant only to a test folder in a `utils.py` file within that folder. Import using relative imports: `from .utils import TodoTestRecord`. Note: `utils.py` is internal to its test folder. If a utility is needed outside that scope, place it under `test/utils/` and export via `__init__.py`. Only these two locations are acceptable for test utilities.

### Ad-Hoc Test Utilities
Classes, models, or helper functions defined for a single test file's purposes (e.g., test input models, mock schemas, sample records, assertion helpers) should remain in that test file. Only move to `utils.py` when the same utility is needed across multiple test files within the folder.
The same applies to fixtures specific to a test file.

### Fixtures
- Use `pytest` fixtures for setting up test data, mocks, and common configurations.
- When writing fixtures, **YOU MUST ALWAYS** use an appropriate scope. ALWAYS prefer function, unless the fixture creates a heavy resource, such as a docker container or some runtime service- in which case prefer session scoped fixtures. The isolation will be handled by other fixtures(e.g. schema isolation, temp directories, etc.).

### Fixture Location
- Place common fixtures used across multiple test files in `test/fixtures/` and export them via `test/fixtures/__init__.py`. import them via the root conftest..py file to make them available globally.
- API's returned from fixtures under `test/fixtures` must be defined under `test/utils/` and imported into the fixture file as well as test files as needed.
- For fixtures specific to a single test folder, place them in a `conftest.py` file within that folder.
- For fixtures specific to a single test file, define them within that test file.

# Test Anatomy

### Naming Convention
Use BDD-style naming: `test_should_<expected_behavior>_when_<condition>`.
- Bad: `test_feature_calculation`
- Good: `test_should_mark_todo_as_overdue_when_due_date_passed`

### Anatomy
Follow the **AAA** / **Arrange-Act-Assert** pattern in all tests:
1. **Arrange**: Set up the data, fixtures, configuration, and **expected results**.
2. **Act**: Execute the function or job under test.
3. **Assert**: Verify the results and side effects.
Separate these sections with blank lines for readability.


### Contextual Assert Messages
**NON-NEGOTIABLE:** Every assertion **MUST ALWAYS** include a custom failure message explaining the **business impact** or the **functional requirement** that was violated. Avoid generic "expected X got Y" messages; instead, explain *what* the data represents and *why* the mismatch matters. Every assertion **MUST ALWAYS** include a contextual message. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

**Pattern (Good)**: Message explains business impact.
```python
assert actual == expected, (
    "Order total mismatch: Customer would be charged incorrect amount. "
    "Verify tax calculation and discount application logic."
)
```

### Float Comparison
You **MUST ALWAYS** Use `pytest.approx` for comparing floating-point values. When testing exact numeric values (not thresholds), compute the expected value precisely rather than approximating.

**Pattern (Good)**: Use pytest.approx for float assertions.
```python
import pytest

def test_should_calculate_average_completion_time_when_todos_completed(todo_repository):
    # Arrange
    completion_times = [45.5, 30.0, 24.5]  # minutes
    expected_avg = sum(completion_times) / len(completion_times)  # 33.333...

    # Act
    result = calculate_average_completion_time(todo_repository)

    # Assert - use pytest.approx for float comparison
    assert result == pytest.approx(expected_avg), (
        "Average completion time calculation is incorrect"
    )

    # For multiple floats, pytest.approx works on lists too
    assert actual_times == pytest.approx(completion_times, rel=1e-6), (
        <contextual assert message>
    )
```

**Anti-Pattern (Bad)**: Hardcoded approximate values without pytest.approx.
```python
# ❌ Hardcoded magic number - where did 33.33 come from?
assert result == 33.33

# ❌ Direct float comparison - fails due to floating point precision
assert result == 33.333333333333336
```

### Comprehensive Assertions
When asserting on collections (lists, sets), verify ALL elements—not a subset.
When asserting on structured data (models, dataframes, dataclasses, dicts), verify ALL fields—not selected ones.
These requirements compound: a list of models must verify all elements AND all fields within each element.

**NON-NEGOTIABLE**: You **MUST ALWAYS** Construct an exact replica of the expected result and compare against the actual result using a single `==` assertion. Field-by-field assertions, element-specific assertions, length-based assertions, or any combination thereof are **UNACCEPTABLE**.

**Pattern (Good)**: Single model equality comparison.
```python
from my_module import MyRecord

expected = MyRecord(
    id="abc",
    name="test",
    value=pytest.approx(42.5),
    count=100,
)

actual: MyRecord = get_record_by_id("abc")

assert actual == expected, <contextual assert message>
```

**Pattern (Good)**: Dict equality comparison.
```python
expected = {
    "order_id": "o1",
    "status": "confirmed",
    "total": pytest.approx(45.0),
    "items": ["p1", "p2"],
}
actual = get_order_summary(order_id="o1")

assert actual == expected, (
    <contextual assert message>
)
```

**Pattern (Good)**: List of models equality comparison.
```python
from my_module import TodoRecord

expected = [
    TodoRecord(id="t1", title="Buy groceries", status="pending"),
    TodoRecord(id="t2", title="Call mom", status="completed"),
    TodoRecord(id="t3", title="Review PR", status="pending"),
]
actual = [TodoRecord.model_validate(row.asDict(recursive=True)) for row in results]

assert actual == expected, (
    <contextual assert message>
)
```

**Pattern (Good)**: Nested structure equality via models.
```python
from my_module import Order, LineItem, ShippingAddress

expected = Order(
    order_id="o1",
    items=[
        LineItem(product_id="p1", quantity=2, unit_price=10.0),
        LineItem(product_id="p2", quantity=1, unit_price=25.0),
    ],
    shipping=ShippingAddress(
        street="123 Main St",
        city="Springfield",
        postal_code="12345",
    ),
    total=45.0,
)

actual = order_repository.get_by_id(order_id="o1")

assert actual == expected, (
   <contextual assert message>
)
```

**Pattern (Good)**: DataFrame equality via list of models.
```python
from my_module import TodoRecord

expected = [
    TodoRecord(todo_id="t1", title="Buy groceries", priority=1),
    TodoRecord(todo_id="t2", title="Call mom", priority=2),
]
actual_df = get_todos_dataframe(repository)
actual = [
    TodoRecord.model_validate(row.asDict(recursive=True))
    for row in actual_df.collect()
]

assert actual == expected, (
    <contextual assert message>
)
```

**Anti-Pattern (Bad)**: Field-by-field assertions.
```python
# ❌ Verbose, incomplete, and prone to missing fields
# ❌ Also missing contextual assert messages
assert actual.id == "abc"
assert actual.name == "test"
assert actual.value == pytest.approx(42.5)
# Forgot to check 'count' - bug goes undetected!
```

**Anti-Pattern (Bad)**: Length-based assertions only.
```python
# ❌ Only verifies count, not content - wrong data goes undetected
# ❌ Also missing contextual assert message
todos = get_all_todos()
assert len(todos) == 3
# All 3 todos could have wrong titles, statuses, or IDs - test still passes!
```

**Anti-Pattern (Bad)**: Subset/partial key assertions.
```python
result = get_order_summary(order_id="o1")

# ❌ Only checks some keys, ignores critical fields
# ❌ Also missing contextual assert messages
assert result["order_id"] == "o1"
assert result["status"] == "confirmed"
# Forgot to check 'total', 'items', 'shipping_address' - bugs go undetected!
```

**Anti-Pattern (Bad)**: Loop-based individual assertions.
```python
expected_ids = ["t1", "t2", "t3"]
todos = get_all_todos()

# ❌ Iterating assertions miss extra items and field mismatches
# ❌ Also missing contextual assert message
for i, todo in enumerate(todos):
    assert todo.id == expected_ids[i]
# Extra todo at index 3 goes undetected! Wrong titles/statuses go undetected!
```

**Anti-Pattern (Bad)**: DataFrame column-only assertions.
```python
actual_df = process_todos(input_df)

# ❌ Only checks 'status' column, ignores mismatches in other columns
# ❌ Also missing contextual assert message
assert list(actual_df["status"]) == ["pending", "completed"]
# 'priority', 'due_date', 'assignee' columns could be completely wrong!
```

### Reuse
- **Fixtures** are located in `test/fixtures/` and are auto-discovered by `test/conftest.py`.
- **Utility classes** (e.g., `Asset`, `AsyncExecutor`, `ConfigFactory`, `KafkaClient`) are in `test/utils/` and can be imported via `from test.utils import ClassName`.
- Before writing tests, explore `test/fixtures/` for available fixtures and `test/utils/` for utility classes.
- Also check all `conftest.py` files from the test file's folder up to the root test folder.
- Check for a `util.py` in the test file's immediate folder for folder-scoped helpers.
- Check `test/utils/**` for shared utilities available across all tests.
- Do not reinvent fixtures or utilities already defined.

### Code Duplication
**NON-NEGOTIABLE**: When writing tests, you **MUST ALWAYS THINK** about which parts of the test code do not directly relate to the specific test and have potential to be reused in other test suites. Such code **MUST** be extracted to `test/utils/` and exported via `__init__.py`. Duplicating reusable logic across test files is **UNACCEPTABLE**.
