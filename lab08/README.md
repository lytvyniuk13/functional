# Лабораторна робота №8: Алгебраїчні типи даних (ADT) “по-Python’івськи”

## Варіант №9: JSON-подібне дерево

### 1. Мета роботи
- Опанувати моделювання алгебраїчних типів даних (Sum Types) у Python за допомогою `@dataclass(frozen=True)` та `Union` / `TypeAlias`.
- Застосувати звуження типів через `Literal` та структурну типізацію за допомогою `typing.Protocol`[cite: 25].
- Реалізувати структурний pattern matching (`match/case`) для декомпозиції та обробки вкладених деревоподібних структур[cite: 25].
- Забезпечити строгу перевірку типів через `mypy --strict` без помилок[cite: 25].

---

### 2. Реалізація компонентів варіанта №9:
1. **Вузли ADT (`model.py`)**:
   - `JNull`, `JBool(value: bool)`, `JNumber(value: int | float)`, `JString(value: str)`[cite: 25].
   - `JArray(elements: Tuple[JValue, ...])` — незмінний масив[cite: 25].
   - `JObject(fields: Tuple[Tuple[str, JValue], ...])` — незмінний об'єкт[cite: 25].
   - Рекурсивний псевдонім: `JValue: TypeAlias = Union[JNull, JBool, JNumber, JString, JArray, JObject]`[cite: 25].
2. **Використання `Literal`**:
   - `RenderMode: TypeAlias = Literal["compact", "pretty"]` обмежує режим форматування JSON[cite: 25].
3. **Структурний контракт `Protocol`**:
   - `JSONNodeProtocol` декларує інтерфейс із методами `node_count()` та `depth()`[cite: 25].
4. **Чисті операції (`evaluator.py`, `pretty.py`)**:
   - `count_nodes(node)` — підрахунок загальної кількості вузлів[cite: 25].
   - `max_depth(node)` — максимальна глибина вкладеності[cite: 25].
   - `render(node, mode)` — рендеринг у валідний JSON-текст[cite: 25].
   - `to_native(node)` та `from_native(data)` — конвертація у/з нативних типів Python[cite: 25].

---

### 3. Інструкція із запуску

#### Встановлення залежностей:
```powershell
python -m pip install -r requirements.txt