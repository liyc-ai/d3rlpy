import argparse
import d3rlpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=str, default='breakout')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--gpu', type=int)
    args = parser.parse_args()

    # fix seed
    d3rlpy.seed(args.seed)

    dataset, env = d3rlpy.datasets.get_atari_transitions(
        args.game,
        fraction=0.01,
        index=1 if args.game == "asterix" else 0,
    )

    env.seed(args.seed)

    bcq = d3rlpy.algos.DiscreteBCQ(
        learning_rate=5e-5,
        optim_factory=d3rlpy.models.optimizers.AdamFactory(eps=1e-2 / 32),
        batch_size=32,
        q_func_factory=d3rlpy.models.q_functions.QRQFunctionFactory(
            n_quantiles=200),
        scaler="pixel",
        n_frames=4,
        target_update_interval=2000,
        reward_scaler=d3rlpy.preprocessing.ClipRewardScaler(-1.0, 1.0),
        action_flexibility=0.3,
        beta=0.01,
        use_gpu=args.gpu)

    env_scorer = d3rlpy.metrics.evaluate_on_environment(env, epsilon=0.001)

    bcq.fit(
        dataset,
        eval_episodes=[None],  # dummy
        n_steps=50000000 // 4,
        n_steps_per_epoch=125000,
        save_interval=10,
        scorers={
            'environment': env_scorer,
        },
        experiment_name=f"DiscreteBCQ_{args.game}_{args.seed}")


if __name__ == '__main__':
    main()