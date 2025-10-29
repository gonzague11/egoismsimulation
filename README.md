# egoismsimulation
The objective of this program is to study, in a simple environment, the interaction between people with different levels of egoism. We run a simulation where people need to eat to survive and reproduce, and they can team up to hunt, giving them more food. The repartition of the cows they hunt is determined by the 2 levels of egoism.

In the first program, there is at the beginning 1 man. Each day there are 1000 carrots, the man walks randomly and collects carrots. If he collects more than 5 carrots in a day he survives, otherwise he dies, and, after the 5 first carrots (used to survive), each 5 carrots are used to reproduce himself. Example : if he collects 23 carrots, he survives, and gives birth to 3 children ((23-5) // 5). Since the number of carrots is limited, there is a maximum capacity, which is quickly reached. In day 20, we add cows, that represent 10 food unities, but need 2 people to take them down. When 2 people kill a cow, they take 5 food unities each. There is at the beginning 15 cows, and, when a cow is killed, the program waits 1/5th of a day to put an other cow. Same as before, the number of cows can't exceed 75 per day, so there is a maximum capacity, which is also quickly reached.

In the second program, the initial situation is the ending of the first one, the population is already at the maximum capacity, and we introduce the game theory part. Now, each human has a egoism level (from 1 to 9), and, when 2 humans kill a cow, the repartition is determined by the egoism level. 
The egoism level represents the number of food unities each human is wanting after killing a cow. The repartition is made following these rules :
-If egoism level are complementary (i.e the sum is 10, for example 7 and 3, each human gets what he asked for)
-If egoism level are too low (i.e sum is below 10, for example 6 and 2, each human gets what he asked for, and the reste is splitted between them (if the rest is odd, the more egoist takes one more)
-If egoism level are too high (i.e sum is above 10, each one loses the exceed, plus a malus of one food unity. For example, with 8 and 5, the sum is 13, so everyone loses 3, plus the malus of 1, everyone loses 4, so the repartition is 4 and 1, there's a ressource loss)

The objective is now to see which profile will survive the most in this environment.

At the beginning, the most egoist profiles do perform well, ans the less egoist profiles perform very bad, simply because they get practically no food).
As soon as there is no more profile with egoism level at 1, it becomes unefficient to have a profile at 9, because you're sure to be in conflict at every food repartition, and then to lose ressources. So the disparition of the low egoism profiles makes the high egoism profiles unefficient, and then they don't survive.

We observe that in the end, there is a high concentration between the middle profiles (4-5-6), meaning that the Nash Equilibrium is everyone with an egoism level of 5 : if everyone is at 5, there's no reason to go down (you'll just get less food), an no reason to go higher (this would create conflict and then ressources loss).
