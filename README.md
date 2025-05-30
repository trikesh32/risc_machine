# Рисковая машинка)
- Трикашный Михаил Дмитриевич P3206
- Вариант: `asm | risc | harv | mc | tick | binary | stream | mem | cstr | prob1 | vector`
- Расшифровка:
  - `asm`: синтаксис ассемблера. Необходима поддержка `label`-ов, секций и директивы `.org`. Поддержка пользовательских макроопределений. 
  - `risc`: система команд должна быть упрощенной, в духе RISC архитектур
    -  Стандартизированная длина команд.
    -  Операции над данными осуществляются только в рамках регистров.
    -  Доступ к памяти и ввод-вывод -- отдельные операции
  - `harv`: Гарвардская архитектура
  - `mc`: команды реализованы с помощью микрокоманд
  - `tick`: процессор необходимо моделировать с точностью до такта, процесс моделирования может быть приостановлен на любом такте.
  - `binary`: бинарное представление машинного кода
  - `stream`: Ввод-вывод осуществляется как поток токенов.
  - `mem`: порты ввода-вывода отображаются в память и доступ к ним осуществляется штатными командами
  - `cstr`: Null-terminated (C string)
  - `prob1`: Euler problem 4 [link](https://projecteuler.net/problem=4)
  - `vector`: векторная организация процессора (понятие не имею что бы это значило)

# Набор инструкций
- ``

# Кодирование инструкций
Для команд с тремя регистровыми аргументами формируется такое машинное слова:
```text
┌─────────┬─────────┬─────────┬─────────┬───────────────────────────────┐
│ 31...27 │ 26...23 │ 22...19 │ 18...15 │ 14                          0 │
├─────────┼─────────┼─────────┼─────────┼───────────────────────────────┤
│  опкод  │   арг1  │   арг2  │   арг3  │       не используется         │
└─────────┴─────────┴─────────┴─────────┴───────────────────────────────┘
```
Для команд с двумя регистровыми аргументами и `immediate` значением в качестве аргумента (для команд по типу `mv` биты 18...0 не используются)
```text
┌─────────┬─────────┬─────────┬─────────────────────────────────────────┐
│ 31...27 │ 26...23 │ 22...19 │ 18                                    0 │
├─────────┼─────────┼─────────┼─────────────────────────────────────────┤
│  опкод  │   арг1  │   арг2  │                   k                     │
└─────────┴─────────┴─────────┴─────────────────────────────────────────┘
```
Для команд с одним регистровым аргументом и `immediate` значением в качестве аргумента
```text
┌─────────┬─────────┬───────────────────────────────────────────────────┐
│ 31...27 │ 26...23 │ 22                                              0 │
├─────────┼─────────┼───────────────────────────────────────────────────┤
│  опкод  │   арг1  │                        k                          │
└─────────┴─────────┴───────────────────────────────────────────────────┘
```
Для команд с без регистровых аргументов и `immediate` значением
```text
┌─────────┬─────────┬─────────┬─────────────────────────────────────────┐
│ 31...27 │ 26...23 │ 22...19 │ 18                                    0 │
├─────────┼─────────┼─────────┼─────────────────────────────────────────┤
│  опкод  │ не испл │ не испл │                   k                     │
└─────────┴─────────┴─────────┴─────────────────────────────────────────┘
```
Опкоды операций:
- `00000` (0x00) - `lui`
- `00001` (0x01) - `mv`
- `00010` (0x02) - `sw`
- `00011` (0x03) - `lw`
- `00100` (0x04) - `addi`
- `00101` (0x05) - `add`
- `00110` (0x06) - `sub`
- `00111` (0x07) - `mul`
- `01000` (0x08) - `mulh`
- `01001` (0x09) - `div`
- `01010` (0x0a) - `rem`
- `01011` (0x0b) - `sll`
- `01100` (0x0c) - `srl`
- `01101` (0x0d) - `and`
- `01110` (0x0e) - `or`
- `01111` (0x0f) - `xor`
- `10000` (0x10) - `j`
- `10001` (0x11) - `jal`
- `10010` (0x12) - `jr`
- `10011` (0x13) - `blt`
- `10100` (0x14) - `ble`
- `10101` (0x15) - `bgt`
- `10110` (0x16) - `bge`
- `10111` (0x17) - `beq`
- `11000` (0x18) - `bne`
- `11001` (0x19) - `halt`

Коды регистров:
- `0000` (0x0) - `zero`
- `0001` (0x1) - `r0`
- `0010` (0x2) - `r1`
- `0011` (0x3) - `r2`
- `0100` (0x4) - `r3`
- `0101` (0x5) - `r4`
- `0110` (0x6) - `r5`
- `0111` (0x7) - `r6`
- `1000` (0x8) - `sp`

# Регистры
Доступные программисту:
`Zero` `r0` `r1` `r2` `r3` `r4` `r5` `r6` `Sp`
Недоступные программисту: `Ar` `Pc` `Mc` `Mr` `Pr`
- `Zero` - 32х битный регистр, всегда возвращает 0
- `r0` - `r6` - 32х битные регистры общего назначения
- `Sp` - 32х битный регистр общего назначения, но по лору это stack pointer
- `Ar` - регистр, хранящий в себе адрес памяти данных
- `Pc` - регистр, хранящий в себе адрес памяти инструкций
- `Mc` - регистр, хранящий в себе адрес памяти микрокоманд
- `Mr` - регистр, хранящий в себе микрокоманду, по адресу в `Mc`
- `Pr` - регистр, хранящий в себе инструкцию для выполнения

# АЛУ
Поговорим об АЛУ. В моей модели оно довольно "жирненькое". Режимы АЛУ:
- `0000`: `Сложение` - складывает два числа с шины первого аргумента и второго аргумента и выводит результат на шину результата.
- `0001`: `Вычитание` - вычитает число с шины второго аргумента из числа с шины первого аргумента и выводит результат на шину результата.
- `0010`: `Умножение (младшие 4 байте)` - перемножает числа с шин аргументов и выводит младшие 4 байта на шину результата.
- `0011`: `Умножение (старшие 4 байта)` - перемножает числа и выводит старшие 4 байта
- `0100`: `Деление` - целочисленно делит два числа
- `0101`: `Остаток от деления` - выводит на шину результата остаток от деления.
- `0110`: `Логический сдвиг влево` - побитого сдвигает первый аргумент влево
- `0111`: `Логический сдвиг вправо` - побитого сдвигает первый аргумент на второй аргумент вправо
- `1000`: `Побитовое AND` - побитого применяет конъюнкцию.
- `1001`: `Побитовое OR` - побитого применяет дизъюнкцию
- `1010`: `Побитовок XOR` - применяет побитого ИСКЛ-ИЛИ

# Модуль условий
В моей модели для переходов используется отдельный модуль условий. Ему на вход подается режим работы и два аргумента. На выходе один бит выполнения условия (0 если не выполняется, 1 если выполняется). Режимы работы:
- `0000`: `Равенство` - возвращает 1 если два числа равны, 0 в противном случае
- `0001`: `Неравенство` - возвращает 1 если два числа неравны, 0 в противном случае
- `0010`: `Меньше` - возвращает 1 если A < B, 0 иначе.
- `0011`: `Меньше или равно` - возвращает 1 если A <= B, 0 иначе
- `0100`: `Больше` - возвращает 1 если A > B, 0 иначе
- `0101`: `Больше или равно` - возвращает 1 если A >= B, 0 иначе

# Модуль памяти данных
Так как IO реализуется через MMIO, для его реализации написан отдельный модуль обращений к памяти данных.



# Устаревшие идеи которые немного жаль терять (кажутся интересными)
Одна инструкция состоит из 4 байт (32 бит)
- Старший байт (4ый байт) - опкод
- 3ий байт - регистр возврата. Пример:
  - `00010000` - регистр r1
  - `00110000` - регистр r3
- 2ой байт - первый операнд. Пример:
  - `00010000` - регистр r1
  - `00110000` - регистр r3
- Младший байт (1ый байт) - второй операнд. Пример:
  - `00010000` - регистр r1
  - `00110000` - регистр r3

Подробнее про старший байт (опкод):
- 8ой бит (старший):
  - при активации команда берет в операнда младшие 20 бит как `immediate` (используется в `lui` - Load Upper Immediate)
- 7ой бит:
  - при активации команда берет в качестве аргумента младшие 12 бит как `immediate` (используется в командах `addi` или `subi`)
- 6ой бит:
  - при активации обозначает инструкцию перехода (подробнее ниже)
- 5ый бит:
  - при активации обозначает инструкцию обращения к памяти (подробнее ниже)
- младшие 4 бит - дополнительная информация об инструкции:
  - `0000` - `add`, при активации бита перехода - `beq`, при активации бита обращения к памяти - `lw`
  - `0001` - `sub`, при активации бита перехода - `bne`. при активации бита обращения к памяти - `sw`
  - И так далее (подробнее ниже)
- При активации всех старших 4х бит опкода, инструкция интерпретируется как `halt` 