# what are decorators


## quick idea

a decorator takes a functon and gives it extra stuff to do without changing the real code inside


## functons in python

in python a functon is just like a normal variabl

- you can put a functon in a variabl

- you can give a functon to anoter functon as an input

- a functon can make an other functon and return it


## functon inside functon

you can just write a small functon inside a bigger functon



## the at sign

the @ symbol is just a lazy shortcut

instead of typing

my_functon = my_decorator(my_functon)


you just write

@my_decorator

on top of your functon


## args and kwargs

star args and two star kwargs let the wrap functon take any inputs so nothing crashes


## functools wraps

always put functools wraps on the wrapper

if you forget it the functon forgets its own name and help text