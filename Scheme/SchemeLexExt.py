{
	'datum':
		p_or(
			p_type('simple datum'),
			p_type('compound datum'),
		),
	'simple datum':
		p_or(
			p_type('boolean'),
			p_type('number'),
			p_type('character'),
			p_type('string'),
			p_type('symbol'),
		),
	'symbol':
		p_type('identifier'),
	'compound datum':
		p_or(
			p_type('list'),
			p_type('vector'),
		),
	'list':
		p_or(
			p_chain(
				p_re(r'('),
				p_or(
					p_star(p_type('datum')),
					p_chain(
						p_plus(p_type('datum')),
						p_re(r'\.'),
						p_type('datum'),
					),
				),
				p_re(r')'),
			),
			p_type('abbreviation'),
		),
	'abbreviation':
		p_chain(
			p_type('abbrev prefix'),
			p_type('datum'),
		),
	'abbrev prefix':
		p_re(r"['`,]|,@"),
	'vector':
		p_chain(
			p_re(r'#('),
			p_star(p_type('datum')),
			p_re(r')'),
		),
	
	
	'expression':
		p_or(
			p_type('variable'),
			p_type('literal'),
			p_type('procedure call'),
			p_type('lambda expression'),
			p_type('conditional'),
			p_type('assignment'),
			p_type('derived expression'),
			p_type('macro use'),
			p_type('macro block'),
		),
	'literal':
		p_or(
			p_type('quotation'),
			p_type('self-evaluating'),
		),
	'self-evaluating':
		p_or(
			p_type('boolean'),
			p_type('number'),
			p_type('character'),
			p_type('string'),
		),
	'quotation':
		p_or(
			p_chain(
				p_re(r"'"),
				p_type('datum'),
			),
			p_chain(
				p_re(r'(quote'),
				p_type(r'datum'),
				p_re(r')')
			),
		),
}
