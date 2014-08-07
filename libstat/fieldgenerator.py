from mongodbforms.fieldgenerator import MongoFormFieldGenerator

class FormFieldGenerator(MongoFormFieldGenerator):
    
    def get_field_choices(self, field):
        """
            Overridden to get rid of defaulting to include blank_choice
        """
        return super(FormFieldGenerator, self).get_field_choices(field, include_blank=False)
