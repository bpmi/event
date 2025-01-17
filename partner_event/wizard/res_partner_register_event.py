# Copyright 2015 Tecnativa - Javier Iniesta
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2018 Jupical Technologies Pvt. Ltd. - Anil Kesariya
# Copyright 2020 Tecnativa - Víctor Martínez
# Copyright 2014-2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerRegisterEvent(models.TransientModel):
    _name = "res.partner.register.event"
    _description = "Register partner for event"

    event = fields.Many2one(
        comodel_name="event.event", required=True, ondelete="cascade"
    )

    def _prepare_registration(self, partner):
        return {
            "event_id": self.event.id,
            "partner_id": partner.id,
            "attendee_partner_id": partner.id,
            "name": partner.name,
            "email": partner.email,
            "phone": partner.phone,
            "date_open": fields.Datetime.now(),
        }

    def button_register(self):
        vals_list = []
        Registration = self.env["event.registration"]
        active_ids = self.env.context.get("active_ids", [])
        if self.env.context.get("active_model", "") == "event.registration":
            registrations = self.env["event.registration"].browse(active_ids)
            partners = registrations.attendee_partner_id
            partners += registrations.filtered(
                lambda x: not x.attendee_partner_id
            ).partner_id
        else:
            partners = self.env["res.partner"].browse(active_ids)
        for partner in partners:
            if not Registration.search(
                [
                    ("event_id", "=", self.event.id),
                    "|",
                    ("attendee_partner_id", "=", partner.id),
                    "&",
                    ("attendee_partner_id", "=", False),
                    ("partner_id", "=", partner.id),
                ]
            ):
                vals_list.append(self._prepare_registration(partner))
        self.env["event.registration"].create(vals_list)
