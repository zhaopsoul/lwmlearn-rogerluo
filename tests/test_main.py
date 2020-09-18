# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 15:26:59 2019

@author: rogerluo
"""

import warnings
warnings.filterwarnings("ignore")

import pytest
import traceback
from lwmlearn import pipe_main, LW_model
from sklearn.datasets import make_classification, make_regression

from lwmlearn.utilis.testing import runlocaldataset
from lwmlearn.dataset import get_local_data

# %% data fixtures
@pytest.fixture
def data0():
    '''retrun fake classification data
    '''
    X, y = make_classification(100, n_features=25, n_informative=15, shift=100)
    return X, y

@pytest.fixture
def data1():
    '''return fake regression data
    '''
    X, y = make_regression(100, n_features=25, n_informative=15)
    
    return X, y

@pytest.fixture
def datar():
    '''return kaggle give me some credit data
    '''
    data = get_local_data('givemesomecredit.csv')
    y = data.pop('y')
    X = data
    
    return X, y

@pytest.fixture
def testing_path():
    '''
    '''
    import pathlib2
    
    return pathlib2.Path('TestResults')

# %% tesing items

def test_fit_transform(data0, data1):
    '''test  fit/transform/resample for all pipelines generated by pipe_main
    
    meta estimator will be ignored
    '''
    X0, y0 = data0
    X1, y1 = data1
   
    all_d = pipe_main()
    operator_set = []
    for i in all_d['default'].values():
        operator_set.extend(i)
    
    for i in all_d['predefined'].values():
        operator_set.extend(i)
    operator_set = set(operator_set)
    
    # test
    check = 0
    n = []
    for i in operator_set:
        p = pipe_main(i)
        if hasattr(p, '_estimator_type'):
            if p._estimator_type == 'classifier':
                X, y = X0, y0
            else:
                X, y = X1, y1
                
            try:
                if hasattr(p, 'fit'):
                    p.fit(X, y=y)
                if hasattr(p, 'transform'):
                    p.transform(X)
                if hasattr(p, 'resample'):
                    p.resample(X, y)
            except Exception:
                traceback.print_exc()
                check -= 1
                n.append(i)
    
    if check < 0:
        print('{} operators failed <test_fit_transform> \n'.format(n))
        print("failed operators are {}".format(n))
    
    assert check == 0       

def test_runautoML(testing_path):
    '''
    test runautoML for local data set
    '''
    check = 0
    try:
        runlocaldataset(
            'givemesomecredit.csv',
            dirs=testing_path,
            sample=5000,
            out_searchstep=False,
            is_search=True,
            kind='bayesiancv',
            model_list=[
                'cleanNA_woe8_fxgb_TomekLinks_XGBClassifier',
                'cleanNA_woe8_fxgb_inlierLocal_NeighbourhoodCleaningRule_SGDClassifier',
            ],
        )
    except:
        traceback.print_exc()
        check = -1

    assert check == 0
        
def test_LW_model_method(datar, testing_path):
    '''test LW_model method using real data
    '''
    
    path = testing_path / 'lw_model_method'
    # test
    check = 0
    X, y = datar
    try:
        m = LW_model('clean_oht_frf_OneSidedSelection_XGBClassifier', 
                      path=path,
                      verbose=2)
        # fit the model
        m.fit(X, y)
        # predict
        m.predict(X)
        # calculate evaluation metrics
        m.test_score(X, y, cv=1, scoring=['KS', 'roc_auc'])
        m.cv_validate(X, y, scoring=['roc_auc', 'KS'])
        # plot auc curve
        m.plot_auc(X, y, cv=4)
        # plot lift curve
        m.plot_lift(X, y, max_leaf_nodes=10)
        # predict by integer index
        m.predict(X, pre_level=True)
        # hyper-parameter tuning, search param_grid space
        m.opt_sequential((X, y), kind='bayesiancv')
        # plot search learning curve
        m.plot_gridcv(m.kws_attr['gridcvtab'][0])
        # plot cv score path
        m.plot_cvscore(X, y, False, cv=5)
        # plot lift and auc together
        m.plot_AucLift(X, y, fit_train=False)
        
        m.run_analysis((X, y))
        
    except:
        traceback.print_exc()
        check = -1
    assert check == 0
    

# def test_clean(testing_path):
#     '''
#     '''
#     import shutil
    
#     shutil.rmtree(testing_path)
    

