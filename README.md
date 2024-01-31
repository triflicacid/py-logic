# Python: Logic

A basic logic application in Python

Supports the following:
- Create basic logic formulae.
- Parse basic logic formulae.
- Create truth tables for formulae.
- Evaluate formulae.
- Convert propositions to CNF and DNF.

The following will be implemented:
- Tautology detection via resolution and/or simple tableau.

## CLI
The file `cli.py` is a basic command-line interface application for testing and demonstrating this library's abilities.

## Parsing
Formulae are in the form: `<lit/group> [[!]<op> <lit/group>]` where
- `<lit>` is a literal: top, bottom, or a symbol. These may be negated.
- `<group>` is a group, either `(...)` for a compound formula, `[...]` for generalised disjunction, or `<...>` for generalised conjunction. These may be negated.
- `<op>` is an operator. These may be preceded by a negation to produce the negated variant.

**Literals**
- Bottom (false): `F`, `⊥`, `0`.
- Top (true): `T`, `⊤`, `0`.
- Symbol (variable): in the form `[a-zA-Z][a-zA-z0-9]*`.

**Negation**: `!`, `¬`, `~`. Used to negate literals, groups, or operators.

**Binary Connectives**
- Conjunction (Or): `+`, `|`, `v`.
- Disjunction (And): `.`, `&`, `^`.
- Implication: `->`.
- Equality: `=`.
- Xor: `(+)`.
- Reverse Implication: `<-`.
