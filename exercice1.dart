//  EXERCICE 1 : Construire sa propre fonction d'ordre supérieur
//
//  Objectif : Écrire une fonction processList qui prend une liste
//  d'entiers et un prédicat (Int) -> Boolean, et retourne une
//  nouvelle liste contenant uniquement les éléments qui satisfont
//  le prédicat.

List<int> processList(List<int> numbers, bool Function(int) predicate) {
  return numbers.where(predicate).toList();
}

void main() {
  final nums = [1, 2, 3, 4, 5, 6];

  // Tester avec le prédicat "nombres pairs"
  final even = processList(nums, (it) => it % 2 == 0);
  print("Nombres pairs : $even"); // [2, 4, 6]

  // Tester avec le prédicat "nombres > 3"
  final greaterThan3 = processList(nums, (it) => it > 3);
  print("Nombres > 3 : $greaterThan3"); // [4, 5, 6]
}
