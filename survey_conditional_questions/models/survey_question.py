##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)



class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    conditional = fields.Boolean(
        'Conditional Question',
        copy=False,
        # we add copy = false to avoid wrong link on survey copy,
        # should be improoved
    )

    or_and = fields.Boolean(
        '¿Debe cumplir todas las condiciones?',
        copy=False,
        help="Si está con check, todas las preguntas de la condición deben cumplir igualdad, de lo contario, solo una debe cumplir"
        # we add copy = false to avoid wrong link on survey copy,
        # should be improoved
    )

    question_conditional_id = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_2 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_2 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_3 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_3 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_4 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_4 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_5 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_5 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_6 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_6 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_7 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_7 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    question_conditional_id_8 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_8 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )            

    question_conditional_id_9 = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id), ('question_type', 'in', ['multiple_choice', 'simple_choice'])]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_id_9 = fields.Many2one(
        'survey.label',
        'Answer',
        copy=False,
    )

    def validate_upload_file (self, post, answer_tag): 
        self.ensure_one()
        errors = {}
        answer = post[answer_tag]; 
        print("LA PREGUNTA: ", answer)
        
        return errors
    def validate_rut(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        answer = post[answer_tag].strip()
        # Empty answer to mandatory question
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})     
        return errors    

    def validate_ordered_answer(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        answer = post[answer_tag].strip()
        # Empty answer to mandatory question
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})     
        return errors          

    def validate_question(self, post, answer_tag):
        ''' Validate question, depending on question
        type and parameters '''
        self.ensure_one()
        try:
            checker = getattr(self, 'validate_' + self.question_type)
        except AttributeError:
            _logger.warning(
                checker.type +
                ": This type of question has no validation method")
            return {}
        else:
            # TODO deberiamos emprolijar esto
            return checker(post, answer_tag)

