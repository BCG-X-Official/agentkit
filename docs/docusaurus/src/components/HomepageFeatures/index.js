import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Quickly build high quality Agent apps',
    Svg: () => <span style={{fontSize: '100px'}}>🚀</span>,
    description: (
      <>
        Build a strong app in a few hours using a modular, easy to configure tech stack
        based on FastAPI/Nextjs and a library of useful GenAI tools
      </>
    ),
  },
  {
    title: 'Flexible, reactive UI/UX designed for Agents',
    Svg: () => <span style={{fontSize: '100px'}}>💻</span>,
    description: (
      <>
        React/Nextjs chat-based UI that is easy to configure, with features such as streaming,
        rendering of tables/visualizations/code, status of Agent actions and more
      </>
    ),
  },
  {
    title: 'Focus on reliability',
    Svg: () => <span style={{fontSize: '100px'}}>🛡️</span>,
    description: (
      <>
        Easy to configure routing architecture gives control of possible paths Agent can take,
        increasing reliability and making it suited for real-life use cases
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {typeof Svg === 'string' ? Svg : <Svg className={styles.featureSvg} role="img" />}
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
