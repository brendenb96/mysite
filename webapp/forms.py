from django.forms import ModelForm, PasswordInput
from models import Miner
from django import forms

class PoolForm(forms.Form):
    pool_num = forms.CharField(max_length=10)
    pool = forms.CharField(max_length=100)
    user = forms.CharField(max_length=100)
    passw = forms.CharField(max_length=100)

## Excludes will be used
class MinerForm(ModelForm):
    class Meta:
        model = Miner
        widgets = {
        'password': PasswordInput(),
        'sshpassword' : PasswordInput()}
        exclude = ['pool_one','pool_two','pool_three','hash_rate','asic1',
        'asic2','asic3','chain_1_temp','chain_2_temp','chain_3_temp' ,'uptime','name',
        'pool_one_worker','pool_one_password','pool_two_worker','pool_two_password',
        'pool_three_worker','pool_three_password','bitmain_vil','bitmain_freq']