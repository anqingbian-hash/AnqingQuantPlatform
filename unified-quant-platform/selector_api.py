@app.route('/api/selector')
@login_required
def stock_selector():
    """智能选股API"""
    if not STRATEGY_AVAILABLE or not selector:
        return jsonify({
            'success': False,
            'message': '选股引擎未启用'
        })

    try:
        max_stocks = int(request.args.get('max_stocks', 100))
        min_score = float(request.args.get('min_score', 20))

        print(f"🎯 开始选股: max_stocks={max_stocks}, min_score={min_score}")

        # 执行选股
        results = selector.scan_market(max_stocks=max_stocks, min_score=min_score)

        # 生成报告
        report = selector.generate_report(results)

        # 转换数据格式
        stocks_serializable = []
        for stock in results:
            stocks_serializable.append({
                'ts_code': stock['ts_code'],
                'symbol': stock['symbol'],
                'name': stock['name'],
                'industry': stock['industry'],
                'price': float(stock['price']),
                'pct_chg': float(stock['pct_chg']) if stock['pct_chg'] is not None else 0.0,
                'vol': int(stock['vol']),
                'amount': float(stock['amount']) if stock['amount'] is not None else 0.0,
                'score': float(stock['score']),
                'level': stock['level'],
                'level_score': int(stock['level_score']),
                'reasons': stock['reasons']
            })

        return jsonify({
            'success': True,
            'message': f'选股完成，找到 {len(results)} 只股票',
            'data': {
                'scanned': max_stocks,
                'stocks': stocks_serializable,
                'report': report
            }
        })

    except Exception as e:
        import traceback
        error_msg = f"选股失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg,
            'data': None
        })
