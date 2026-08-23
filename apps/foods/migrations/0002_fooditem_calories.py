from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='calories',
            field=models.IntegerField(blank=True, help_text='单位：kcal/100g', null=True, verbose_name='卡路里(每100g)'),
        ),
    ]