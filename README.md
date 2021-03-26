# Janggi
Portfolio project for CS162

A command line interpretation of [Janggi (Korean Chess)](http://en.wikipedia.org/wiki/Janggi)

## Techologies
Python 3.8

## Approach
My approach to this project was to tackle broad, fundamental systems first before moving on to specific game mechanics. The first systems implemented were to convert the expected input of the user to a coordinate system that made more sense from my designer perspective and a system for storing locations followed by a terminal GUI outputting those positions for debugging purposes. My system uses one master game class that handles most of the game logic, and separate piece classes that handle logic that is dependant on invidivual pieces. Per requirements of the program, two mechanics are ignored in this program that would be present in a typical Janggi game. The first is the ability for Generals to force a draw by ending their turn in line of sight of the opposing General. In fact, no draw state exists in this program and the game will continue on until a checkmate occurs. The second mechanic is allowing the players to switch the positions of their horses and elephants.
