# Generated by Django 2.2.9 on 2020-01-14 16:32

import aklub.autocom
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0062_auto_20200109_09110'),
        ('flexible_filter_conditions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terminalcondition',
            name='condition',
        ),
        migrations.AddField(
            model_name='automaticcommunication',
            name='event',
            field=models.ForeignKey(blank=True, help_text='Event', null=True, on_delete=django.db.models.deletion.SET_NULL, to='aklub.Event', verbose_name='Event from which are DonorPaymentChannel data selected'),
        ),
        migrations.AlterField(
            model_name='automaticcommunication',
            name='condition',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='flexible_filter_conditions.NamedCondition'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='template',
            field=models.TextField(help_text='Šablona může obsahovat následující proměnné: <br/>{mr|mrs} or {mr/mrs}, $addressment, $name, $firstname, $surname, $street, $city, $zipcode, $email, $telephone, $regular_amount, $regular_frequency, $var_symbol, $last_payment_amount, $auth_token', max_length=50000, null=True, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='age_group',
            field=models.PositiveIntegerField(blank=True, choices=[(2020, 2020), (2019, 2019), (2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015), (2014, 2014), (2013, 2013), (2012, 2012), (2011, 2011), (2010, 2010), (2009, 2009), (2008, 2008), (2007, 2007), (2006, 2006), (2005, 2005), (2004, 2004), (2003, 2003), (2002, 2002), (2001, 2001), (2000, 2000), (1999, 1999), (1998, 1998), (1997, 1997), (1996, 1996), (1995, 1995), (1994, 1994), (1993, 1993), (1992, 1992), (1991, 1991), (1990, 1990), (1989, 1989), (1988, 1988), (1987, 1987), (1986, 1986), (1985, 1985), (1984, 1984), (1983, 1983), (1982, 1982), (1981, 1981), (1980, 1980), (1979, 1979), (1978, 1978), (1977, 1977), (1976, 1976), (1975, 1975), (1974, 1974), (1973, 1973), (1972, 1972), (1971, 1971), (1970, 1970), (1969, 1969), (1968, 1968), (1967, 1967), (1966, 1966), (1965, 1965), (1964, 1964), (1963, 1963), (1962, 1962), (1961, 1961), (1960, 1960), (1959, 1959), (1958, 1958), (1957, 1957), (1956, 1956), (1955, 1955), (1954, 1954), (1953, 1953), (1952, 1952), (1951, 1951), (1950, 1950), (1949, 1949), (1948, 1948), (1947, 1947), (1946, 1946), (1945, 1945), (1944, 1944), (1943, 1943), (1942, 1942), (1941, 1941), (1940, 1940), (1939, 1939), (1938, 1938), (1937, 1937), (1936, 1936), (1935, 1935), (1934, 1934), (1933, 1933), (1932, 1932), (1931, 1931), (1930, 1930), (1929, 1929), (1928, 1928), (1927, 1927), (1926, 1926), (1925, 1925), (1924, 1924), (1923, 1923), (1922, 1922), (1921, 1921)], null=True, verbose_name='Birth year'),
        ),
        migrations.AlterUniqueTogether(
            name='donorpaymentchannel',
            unique_together={('VS', 'money_account'), ('user', 'event')},
        ),
        migrations.DeleteModel(
            name='Condition',
        ),
        migrations.DeleteModel(
            name='TerminalCondition',
        ),
    ]
