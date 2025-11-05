##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import logging
from odoo.addons.survey.controllers.main import Survey
from odoo import http, SUPERUSER_ID, fields
from odoo.http import request
import json
from odoo.exceptions import UserError
import werkzeug

_logger = logging.getLogger(__name__)
from ..controllers import main as mainController

class SurveyConditional(Survey):
  
    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='http', methods=['POST'], auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers wil be ignored and
        survey state will be forced to 'done'

        TDE NOTE: original comment: # AJAX submission of a page -> AJAX / http ?? """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            # prevent cheating with users creating multiple 'user_input' before their last attempt
            return {}

        if survey_sudo.questions_layout == 'page_per_section':
            page_id = int(post['page_id'])
            questions = request.env['survey.question'].sudo().search([('survey_id', '=', survey_sudo.id), ('page_id', '=', page_id)])
            # we need the intersection of the questions of this page AND the questions prepared for that user_input
            # (because randomized surveys do not use all the questions of every page)
            questions = questions & answer_sudo.question_ids
            page_or_question_id = page_id
        elif survey_sudo.questions_layout == 'page_per_question':
            question_id = int(post['question_id'])
            questions = request.env['survey.question'].sudo().browse(question_id)
            page_or_question_id = question_id
        else:
            questions = survey_sudo.question_ids
            questions = questions & answer_sudo.question_ids

        errors = {}
        # Answer validation
        if not answer_sudo.is_time_limit_reached:
            for question in questions:
                answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                errors.update(question.validate_question(post, answer_tag))

        ret = {}
        retorno = mainController.SurveyConditional().get_conditional(redirect=None, post={"page_id" : post["page_id"], "ids_idq": str(survey_sudo.id), "token" : answer_tag, "alldata" : [post]})
        poped = []
        for n in errors:
            if n + ":hide"  in retorno:
                    poped.append(n)
                    #print("NN2222==>",n) 

        for p in poped:
                errors.pop(p)        

        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            if not answer_sudo.is_time_limit_reached:
                for question in questions:
                    answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                    request.env['survey.user_input_line'].sudo().save_lines(answer_sudo.id, question, post, answer_tag)

            go_back = False
            vals = {}
            if answer_sudo.is_time_limit_reached or survey_sudo.questions_layout == 'one_page':
                answer_sudo._mark_done()
            elif 'button_submit' in post:
                go_back = post['button_submit'] == 'previous'
                next_page, last = request.env['survey.survey'].next_page_or_question(answer_sudo, page_or_question_id, go_back=go_back)
                vals = {'last_displayed_page_id': page_or_question_id}

                if next_page is None and not go_back:
                    answer_sudo._mark_done()
                else:
                    vals.update({'state': 'skip'})

            if 'breadcrumb_redirect' in post:
                ret['redirect'] = post['breadcrumb_redirect']
            else:
                if vals:
                    answer_sudo.write(vals)

                ret['redirect'] = '/survey/fill/%s/%s' % (survey_sudo.access_token, answer_token)
                if go_back:
                    ret['redirect'] += '?prev=prev'

        return json.dumps(ret)
    @http.route()
    def survey_display_page(self, survey_token, answer_token, prev=None, **post):
       
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        UserInput = request.env['survey.user_input']
        user_input = UserInput.with_user(SUPERUSER_ID).search([('token', '=', answer_token)], limit=1)

        if survey_sudo.is_time_limited and not answer_sudo.start_datetime:
            # init start date when user starts filling in the survey
            answer_sudo.write({
                'start_datetime': fields.Datetime.now()
            })

        page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'
        # Select the right page
        if answer_sudo.state == 'new':  # First page
            page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
            data = {
                'survey': survey_sudo,
                page_or_question_key: page_or_question_id,
                'answer': answer_sudo
            }
            data['hide_question_ids'] = UserInput.get_list_questions(
                user_input.survey_id, user_input)
            
            

            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif answer_sudo.state == 'done':  # Display success message
            return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
        elif answer_sudo.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=flag)

            #special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page_or_question_id:
                page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=True)

            data = {
                'survey': survey_sudo,
                page_or_question_key: page_or_question_id,
                'answer': answer_sudo
            }
            
            data['hide_question_ids'] = UserInput.get_list_questions(
                user_input.survey_id, user_input)

            if last:
                data.update({'last': True})

            return request.render('survey.survey', data)
        else:
            return request.render("survey.403", {'survey': survey_sudo})
            # TODO deberiamos heredar esto correctamente

    def equal_answer(self, ans, res):
            if not res:
                return False
            elif ans.id == int(res):
                return True
            else:
                return False

    def compose_key(self, alldata, qid, sid, ans, token):
        res = [sub.get(sid + "_" + str(qid), None) for sub in alldata ]
        res = [i for i in res if i is not None]
        if len(res) == 0:
            res = [sub.get(sid + "_" + str(qid) + "_" + str(ans.id), None) for sub in alldata ]
            res = [i for i in res if i is not None]
        if len(res) == 0:
            input_answer_ids = http.request.env['survey.user_input_line'].with_user(SUPERUSER_ID).search(
                [('user_input_id.token', '=', token),
                 ('question_id', '=', int(qid))])
            if input_answer_ids:
                res = []

                for p in input_answer_ids:
                    if p.question_id.id == int(qid) and p.value_suggested.id == int(ans.id): 
                        res = [int(p.value_suggested)]
                        break
                if len(res) == 0:
                    for p in input_answer_ids:
                        if p.question_id.id == int(qid): 
                            res = [int(p.value_suggested)]
                            break
                        
        if len(res) == 0:                        
            return None
        else:
            return res[0]

    @http.route('/survey_extra/get_conditional', type='json', auth='public',  csrf=False)
    def get_conditional(self, redirect=None, **post):

        data = http.request.params

        print("LA DATA==>",data, "POST==>", post)
        page = None
        try:
            page = int(data["page_id"])
            
        except:    
            page = int(post["post"]["page_id"])
            print("POR ACA SE CVA==>",page )

        try:
            ids = data["ids_idq"].split('_')[0]
        except:    
            ids = post["post"]["ids_idq"].split('_')[0]

        try:
            token =  data["token"]
        except:
            token =  post['post']["token"]
       #idq = data["ids_idq"].split('_')[1]

        try:
            alldata = data["alldata"]
        except:
            alldata = post['post']["alldata"]
        obj_questions = http.request.env['survey.question']
        
        #current_value = None
        
        #if not "@@@TEXT" in data["value"] :
        #   current_value = http.request.env['survey.label'].with_user(SUPERUSER_ID).search([('id','=',data["value"])], limit=1).value
        #else:
        #   current_value = data["value"].replace("@@@TEXT", "")
        question = None
        if page is not None:
            print("ESTA PREGUNTA=>")
            question = obj_questions.with_user(SUPERUSER_ID).search([('survey_id', '=', int(ids)), ('conditional', '=', True) , ('or_and', '=', False), ('page_id', '=', page)])
        else:    
            question = obj_questions.with_user(SUPERUSER_ID).search([('survey_id', '=', int(ids)), ('conditional', '=', True) , ('or_and', '=', False)])
        retorno = []
        for q in question:
            ans = False
            if q.question_conditional_id:
                res = self.compose_key(alldata,str(q.question_conditional_id.id),ids,q.answer_id, token )
                ret = self.equal_answer(q.answer_id, res)
                if ret:
                   ans = True
            if q.question_conditional_id_2:
                res = self.compose_key(alldata,str(q.question_conditional_id_2.id),ids,q.answer_id_2, token)
                ret = self.equal_answer(q.answer_id_2, res)
                if ret:
                   ans = True
            if q.question_conditional_id_3:
                res = self.compose_key(alldata,str(q.question_conditional_id_3.id),ids,q.answer_id_3, token)
                ret = self.equal_answer(q.answer_id_3, res)
                if ret:
                   ans = True
            if q.question_conditional_id_4:
                res = self.compose_key(alldata,str(q.question_conditional_id_4.id),ids,q.answer_id_4, token)
                ret = self.equal_answer(q.answer_id_4, res)
                if ret:
                   ans = True
            if q.question_conditional_id_5:
                res = self.compose_key(alldata,str(q.question_conditional_id_5.id),ids,q.answer_id_5, token)
                ret = self.equal_answer(q.answer_id_5, res)
                if ret:
                   ans = True
            if q.question_conditional_id_6:
                res = self.compose_key(alldata,str(q.question_conditional_id_6.id),ids,q.answer_id_6, token)
                ret = self.equal_answer(q.answer_id_6, res)
                if ret:
                   ans = True
            if q.question_conditional_id_7:
                res = self.compose_key(alldata,str(q.question_conditional_id_7.id),ids,q.answer_id_7, token)
                ret = self.equal_answer(q.answer_id_7, res)
                if ret:
                   ans = True
            if q.question_conditional_id_8:
                res = self.compose_key(alldata,str(q.question_conditional_id_8.id),ids,q.answer_id_8, token)
                ret = self.equal_answer(q.answer_id_8, res)
                if ret:
                   ans = True
            if q.question_conditional_id_9:
                res = self.compose_key(alldata,str(q.question_conditional_id_9.id),ids,q.answer_id_9, token)
                ret = self.equal_answer(q.answer_id_9, res)
                if ret:
                   ans = True


            if ans: 
                retorno.append("{}_{}:show".format(ids, q.id))       
            else:     
                retorno.append("{}_{}:hide".format(ids, q.id))       

        
                question = None
        if page is not None:
            question = obj_questions.with_user(SUPERUSER_ID).search([('survey_id', '=', int(ids)), ('conditional', '=', True) , ('or_and', '=', True), ('page_id', '=', page)])
        else:    
            question = obj_questions.with_user(SUPERUSER_ID).search([('survey_id', '=', int(ids)), ('conditional', '=', True) , ('or_and', '=', True)])
        for q in question:
            ans = True
            if q.question_conditional_id:
                res = self.compose_key(alldata,str(q.question_conditional_id.id),ids,q.answer_id, token)
                ret = self.equal_answer(q.answer_id, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_2:
                res = self.compose_key(alldata,str(q.question_conditional_id_2.id),ids,q.answer_id_2, token)
                ret = self.equal_answer(q.answer_id_2, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_3:
                res = self.compose_key(alldata,str(q.question_conditional_id_3.id),ids,q.answer_id_3, token)
                ret = self.equal_answer(q.answer_id_3, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_4:
                res = self.compose_key(alldata,str(q.question_conditional_id_4.id),ids,q.answer_id_4, token)
                ret = self.equal_answer(q.answer_id_4, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_5:
                res = self.compose_key(alldata,str(q.question_conditional_id_5.id),ids,q.answer_id_5, token)
                ret = self.equal_answer(q.answer_id_5, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_6:
                res = self.compose_key(alldata,str(q.question_conditional_id_6.id),ids,q.answer_id_6, token)
                ret = self.equal_answer(q.answer_id_6, res)
                if not ret:
                   ans = False
            if q.question_conditional_id_7:
                res = self.compose_key(alldata,str(q.question_conditional_id_7.id),ids,q.answer_id_7, token)
                ret = self.equal_answer(q.answer_id_7, res)
                if not ret:
                   ans = False                   
            if q.question_conditional_id_8:
                res = self.compose_key(alldata,str(q.question_conditional_id_8.id),ids,q.answer_id_8, token)
                ret = self.equal_answer(q.answer_id_8, res)
                if not ret:
                   ans = False                   
            if q.question_conditional_id_9:
                res = self.compose_key(alldata,str(q.question_conditional_id_9.id),ids,q.answer_id_9, token)
                ret = self.equal_answer(q.answer_id_9, res)
                if not ret:
                   ans = False                   
            if ans: 
                retorno.append("{}_{}:show".format(ids, q.id))       
            else:     
                retorno.append("{}_{}:hide".format(ids, q.id))       

        print("RETORNOOOOOOOO=>", retorno)
        return retorno