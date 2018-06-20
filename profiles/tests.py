from django.test import TestCase

# Create your tests here.
withdrawable_bank = 100
nonwithdrawable_bank = 50

bank_total = withdrawable_bank + nonwithdrawable_bank

amount = 160

if bank_total > amount:
    if nonwithdrawable_bank > amount:
        nonwithdrawable_bank = nonwithdrawable_bank - amount
    else:
        amount = amount - nonwithdrawable_bank
        nonwithdrawable_bank = 0
        withdrawable_bank = withdrawable_bank - amount
    bank_total = withdrawable_bank + nonwithdrawable_bank
    amount = 0
else:
    raise Exception('My error!')

print("total bank: ", bank_total)
print("Withdrawable bank: ", withdrawable_bank)
print("Nonwithdrawable bank: ", nonwithdrawable_bank)
