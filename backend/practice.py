# perfect numbers
# if the additon of the numbers of the divisoss are equal to the number itsekf .

n=int(input("Enter the number"))
total=0
for i in range(1,n):
    if n%i==0:
        total+=i

if n>1 and total==n:
    print("Yes its a perfect number")
else:
    print("Not a perfect number")