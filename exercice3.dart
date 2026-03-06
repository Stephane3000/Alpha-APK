//  EXERCICE 3 : Traitement de données complexes
//
//  Objectif : Trouver l'âge moyen des personnes dont le prénom
//  commence par 'A' ou 'B', puis afficher le résultat arrondi
//  à une décimale.

class Person {
  final String name;
  final int age;
  Person(this.name, this.age);
}

void main() {
  final people = [
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 35),
    Person("Anna", 22),
    Person("Ben", 28),
  ];

  // Étape 1 — Filtrer les prénoms commençant par 'A' ou 'B'
  final filtered = people
      .where((p) => p.name.startsWith('A') || p.name.startsWith('B'))
      .toList();

  // Étape 2 — Extraire les âges
  final ages = filtered.map((p) => p.age).toList();

  // Étape 3 — Calculer la moyenne
  final double average = ages.reduce((a, b) => a + b) / ages.length;

  // Étape 4 — Afficher arrondi à 1 décimale
  // Détail : Alice(25) + Bob(30) + Anna(22) + Ben(28) = 105 / 4 = 26.25 → 26.3
  print("Âge moyen (A ou B) : ${average.toStringAsFixed(1)}");
}
