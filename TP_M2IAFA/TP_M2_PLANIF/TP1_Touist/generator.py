import itertools as it

fluents = set()
operators = set()

rooms = ['roomG', 'roomD']

# Creation des fluents
for r in rooms:
    fluents.add(f'F_at_robby_{r}')

print(f"$F = [{', '.join(fluents)}]")
print()

# Creation des operateurs
# move_R_S
for r, s in it.product(rooms, rooms):
    if r == s:
        continue
    op_name = f"A_move_{r}_{s}"
    operators.add(op_name)
    print(f"$Cond({op_name}) = [F_at_robby_{r}]")
    print(f"$Add({op_name}) = [F_at_robby_{s}]")
    print(f"$Del({op_name}) = [F_at_robby_{r}]")
    print()
    
print(f"$O = [{', '.join(operators)}]")
