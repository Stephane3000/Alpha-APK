//  EXERCICE 2 : Transformer entre types de collections
//
//  Objectif : À partir d'une liste de chaînes, créer une Map où
//  les clés sont les chaînes et les valeurs sont leurs longueurs.
//  Afficher uniquement les entrées dont la longueur est > 4.

void main() {
  final words = ["apple", "cat", "banana", "dog", "elephant"];

  // Créer la Map  clé -> longueur  (équivalent de associateWith en Kotlin)
  final Map<String, int> wordLengths = {
    for (var word in words) word: word.length
  };

  // Filtrer (longueur > 4) puis afficher
  wordLengths.entries
      .where((entry) => entry.value > 4)
      .forEach((entry) => print("${entry.key} has length ${entry.value}"));
}
