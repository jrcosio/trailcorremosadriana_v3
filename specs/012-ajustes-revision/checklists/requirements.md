# Specification Quality Checklist: Ajustes de la revisión del propietario

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-20
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Revisión (2026-11-20, US1/P6): la instrucción del propietario es inequívoca («siempre»). El
  tratamiento del espacio sobrante (la propia foto oscurecida) se elige para conservar el diseño
  aprobado y se deja escrito. Los fondos decorativos quedan fuera como supuesto explícito,
  ampliable si el propietario lo pide.
- Umbrales: 5 anchos (320–1440), 0 fotos recortadas, 0 incumplimientos AA y 0 px de diferencia en
  los marcos.
- Revisión (2026-11-21, US3/P7): la instrucción del propietario fija qué se sustituye (logo y
  texto en dos filas de la parte superior izquierda) y el objetivo («que se vea bien»). El pie y
  la barra lateral del panel, con fondo oscuro, quedan fuera como supuesto explícito: el logotipo
  tiene el texto oscuro. Umbrales: 0 px de diferencia en la cabecera, 0 desbordamientos, 0
  incumplimientos AA y variantes de 50 KB como máximo. FR-009–FR-012 tienen escenarios en la US3.
- Revisión (2026-11-21, US4/P8): «pon también el logo en el pie» fija el alcance: el pie, no el
  panel. La legibilidad sobre el verde oscuro exige una versión en negativo, derivada sin
  redibujar y sustituible si el propietario aporta una oficial (supuesto explícito). El
  crecimiento de la primera columna está acotado y es medible (FR-014). FR-012 se actualiza para
  no contradecir la US4. Umbrales: 0 px en la cabecera y en la posición horizontal de las columnas
  2.ª a 4.ª, naranja ≥ 3:1, blanco ≥ 4,5:1 y variantes ≤ 50 KB. FR-013–FR-016 tienen escenarios en
  la US4.
- Revisión (2026-11-21, US5/P9): el propietario da el texto literal, así que no hay ambigüedad en
  la frase. El enlace de «JR BLANCO» desaparece porque la frase nueva no lo nombra. Como no hay
  dirección para la Escuela Hacker Cosío, va sin enlace (supuesto explícito y constitución VI).
  Umbrales: 100 % de las páginas públicas, 0 restos de la frase anterior, 0 px de movimiento en la
  cabecera y en la parte superior del pie, 0 desbordamientos y 0 incumplimientos AA. FR-017 y
  FR-018 tienen escenarios en la US5.
- Revisión (2026-11-21, US6/P10): el propietario fija qué se destaca (los tres primeros, cada uno
  con un color suave) y delega los colores. Se eligen oro, plata y bronce (supuesto explícito).
  Lo ambiguo, el podio con filtros, se resuelve con el puesto publicado, sin calcular podios por
  sexo ni por categoría (supuesto ampliable). Umbrales: 100 % de las filas 1–3, tres colores
  distintos, 0 px de diferencia en filas y tablas, contraste ≥ 4,5:1, 0 incumplimientos AA y 0
  desbordamientos. FR-019–FR-021 tienen escenarios en la US6.
- Revisión (2026-11-21, US7 y US8/P11): la US7 es un fallo con un criterio objetivo: se alcanza
  todo, sin desbordamientos, y con altura suficiente queda igual. En la US8, «también aquí» se
  interpreta como el panel, cuya marca antigua está en la barra lateral y en el acceso. El rótulo
  «ADMINISTRACIÓN» se conserva como supuesto reversible. FR-022–FR-025 tienen escenarios en la US7
  y la US8.
- Revisión (2026-11-21, US9/P4): el criterio es objetivo (axe WCAG 2.1 A/AA) y el alcance está
  acotado. Todas las vistas del panel con la sesión iniciada, en tres anchos y en los estados de
  guardado, y sin escrituras reales. Las correcciones se limitan al color, con un tono de la
  paleta. FR-026 y FR-027 tienen escenarios en la US9. Los estados al pasar el ratón y de foco
  quedan fuera, como supuesto explícito.
- Revisión (2026-11-21, US10/P12): el propietario fija el alcance: chicas y chicos de cada prueba,
  y por categoría. Respondió dos preguntas: sin filtros, podio masculino y femenino; presentación
  con una etiqueta junto al nombre. La regla (FR-028) es objetiva y se comprueba con un oráculo
  independiente. El reajuste de columnas que causa la etiqueta se ha medido y queda escrito
  (FR-031). FR-028–FR-031 tienen escenarios en la US10.
- Revisión (2026-11-22, US11/P13): el propietario corrige un literal que la constitución y la
  referencia fijaban. Se enmienda la constitución (1.0.1) y se anota la referencia, sin otras
  consecuencias. «Repasa para que todo esté bien escrito» se acota a todos los textos de la web y
  del panel, y a los mensajes del código. Los contenidos de la organización se revisan, pero no se
  cambian desde el código (constitución IV). Los errores encontrados se enumeran en la US11 y en
  research R11. FR-032–FR-037 tienen escenarios en la US11, y SC-018 y SC-019 son medibles.
- Revisión (2026-11-22, US12): el propietario fija el alcance («que el deploy haga todo») y
  responde tres preguntas: instalación limpia con los CSV de la v2, fotos en disco y usuario
  `organizacion`. Lo que el script no debe hacer queda escrito (FR-039): no sobrescribe datos, no
  cambia contraseñas y no borra volúmenes. FR-038–FR-042 tienen escenarios en la US12, y SC-020 se
  mide con el ensayo local.
