from __future__ import unicode_literals

from django.db import models


class Goal(models.Model):
    # Relational fields
    id = models.AutoField(primary_key=True)
    _parents = models.ManyToManyField('Goal', related_name='_children')
    # Other fields
    description = models.TextField(default='')
    deadline = models.DateTimeField(blank=True, null=True)
    is_achieved = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_savable = self.is_savable()
        if is_savable is True:
            super(Goal, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
            return True
        else:
            return is_savable

    def is_savable(self):
        is_deadline_valid = self.is_deadline_valid()
        if is_deadline_valid is True:
            is_is_achieved_valid = self.is_is_achieved_valid()
            if is_is_achieved_valid is True:
                return True
            else:
                error_message = is_is_achieved_valid[1]
        else:
            error_message = is_deadline_valid[1]

        return False, error_message

    def is_deadline_valid(self):
        # Not saved yet
        if self.id is not None:
            for parent in self._parents.all():
                if self.deadline is None and parent.deadline is None:
                    continue
                if self.deadline is None and parent.deadline is not None:
                    continue
                if self.deadline is not None and parent.deadline is None:
                    return False, 'Deadline before parent'
                if self.deadline is not None and parent.deadline is not None:
                    if self.deadline < parent.deadline:
                        return False, 'Deadline before parent'

            for child in self._children.all():
                if self.deadline is None and child.deadline is None:
                    continue
                if self.deadline is None and child.deadline is not None:
                    return False, 'Deadline after child'
                if self.deadline is not None and child.deadline is None:
                    continue
                if self.deadline is not None and child.deadline is not None:
                    if self.deadline > child.deadline:
                        return False, 'Deadline after child'

            # No objection -> deadline valid
            return True
        else:
            return True

    def is_is_achieved_valid(self):
        if self.id is not None:
            if self.is_achieved is True:
                for parent in self._parents.all():
                    if parent.is_achieved is False:
                        return False, 'This goal is achieved before its parent'
            elif self.is_achieved is False:
                for child in self._children.all():
                    if child.is_achieved is True:
                        return False, 'Child goal is achieved before this'

            # No objection -> is_achieved valid
            return True
        else:
            return True

    def __dfs_for_checking_cycles(self, node, origin_id, at_root=True):
        if not at_root and node.id == origin_id:
            return True
        else:
            for child in node.get_children().all():
                if self.__dfs_for_checking_cycles(child, origin_id, False) is True:
                    return True

    def is_acyclically_valid(self):
        # Assumes the graph before inserting this vertex is acyclic
        if self.id is not None:
            if self.__dfs_for_checking_cycles(self, self.id, True) is not True:
                return True
            else:
                return False, 'Forms cycle'
        else:
            return True

    def get_parents(self):
        return self._parents.all()

    def add_parents(self, parents_list):
        self._parents.add(parents_list)
        is_acyclically_valid = self.is_acyclically_valid()
        if is_acyclically_valid is not True:
            self._parents.remove(parents_list)
        return is_acyclically_valid

    def remove_parents(self, parents_list):
        self._parents.remove(parents_list)

    def get_children(self):
        return self._children.all()

    def add_children(self, children_list):
        self._children.add(children_list)
        is_acyclically_valid = self.is_acyclically_valid()
        if is_acyclically_valid is not True:
            self._children.remove(children_list)
        return is_acyclically_valid

    def remove_children(self, children_list):
        self._children.remove(children_list)

    def get_jobs(self):
        return self._jobs.all()

    def add_jobs(self, jobs_list):
        self._jobs.add(jobs_list)

    def remove_jobs(self, jobs_list):
        self._jobs.remove(jobs_list)

    def __str__(self):
        return str(self.id)