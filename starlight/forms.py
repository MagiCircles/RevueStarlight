from magi.forms import (
    AutoForm,
)
from starlight import models

############################################################
############################################################
# MagiCircles' default collections
############################################################
############################################################

############################################################
############################################################
# Revue Starlight forms
############################################################
############################################################

############################################################
# Voice Actress

class VoiceActressForm(AutoForm):
    class Meta:
        model = models.VoiceActress
        save_owner_on_creation = True
        fields = '__all__'

############################################################
# School

class SchoolForm(AutoForm):
    class Meta:
        model = models.School
        save_owner_on_creation = True
        fields = '__all__'

############################################################
# Stage girl

class StageGirlForm(AutoForm):
    def save(self, commit=False):
        instance = super(StageGirlForm, self).save(commit=False)
        # Make sure all the stage girls have the same year to allow ordering by date
        if instance.birthday:
            instance.birthday = instance.birthday.replace(year=2017)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.StageGirl
        save_owner_on_creation = True
        fields = '__all__'

############################################################
############################################################
# Relive forms
############################################################
############################################################

class CardForm(AutoForm):
    def save(self, commit=False):
        instance = super(CardForm, self).save(commit=False)
        instance.update_cache('stage_girl')
        if commit:
            instance.save()
        return instance

    class Meta(AutoForm.Meta):
        model = models.Card
        save_owner_on_creation = True
        fields = '__all__'
