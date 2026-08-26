# Four-color fox badge

A support-free 2.5D example with an orange base and white, black, and blue top inlays. The black eye/nose dimensions are deliberately parameterized because they are the first details likely to disappear with a large nozzle or aggressive thin-wall processing.

The colored bodies are disjoint: white subtracts black and blue regions, while the orange base subtracts the union of all accents.

Design lesson: semantic regions are easier to maintain and validate than arbitrary face painting, while restricting them to the top band avoids multicolor changes over the full object height.
