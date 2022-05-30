# fst: Finite-State Transducers
### Kenji Sagae

#### Usage
```python
import fst

# Encode a string as an FST, using white space as separator
myfst1 = fst.linear_chain_from_string("This is a test", ' ')

# Create an FST transition by transition
myfst2 = fst.FST()
myfst2.add_transition('w0', 'w0', 'This', 'this', 1)
myfst2.add_transition('w0', 'w0', 'This', 'This', 0)
myfst2.add_transition('w0', 'w0', 'is', 'is', 1)
myfst2.add_transition('w0', 'w0', 'a', 'one', 1)
myfst2.add_transition('w0', 'w0', 'a', 'a', 0)
myfst2.add_transition('w0', 'w0', 'test', 'test', 0)

myfst2.set_initial('w0')
myfst2.set_final('w0')

# Compose the two FSTs
c = fst.compose(myfst1, myfst2)

# Find the shortest paths 
cpaths = c.short_paths(10)
print(cpaths)

# Save the FST
c.save('c.fst')

# Load an FST
newc = fst.load('c.fst')

# Create an inverted FST
invf = fst.inverted(c)

```
