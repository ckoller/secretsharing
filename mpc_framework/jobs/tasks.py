#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务
"""

from app import celery


@celery.task(name='tasks.add_together')
def add_together(a, b):
    print('job tasks.add_together')
    return a + b


@celery.task(name='printy')
def printy(a, b):
    """通过配置文件添加定时任务"""
    print('job printy')
    print(a + b)
    return a + b
