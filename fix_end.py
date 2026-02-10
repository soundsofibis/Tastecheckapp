
if __name__ == '__main__':
    if not API_KEY:
        print('⚠️  WARNING: ANTHROPIC_API_KEY not set!')
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
